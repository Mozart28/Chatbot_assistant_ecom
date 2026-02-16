"""
Admin Backend API - COMPLETE WITH AUTO-EXTRACTION
PDF Upload + Auto Product Detection + Catalog Integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import jwt
import os
from datetime import datetime, timedelta
import json
import re
import subprocess

# PDF Processing - Using pdfplumber (better than PyPDF2)
import pdfplumber

# Use YOUR embedding model (E5) instead of Mistral!
from sentence_transformers import SentenceTransformer

# Use YOUR Pinecone setup
from pinecone import Pinecone

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/admin/*": {"origins": "*"}})

# Configuration
app.config['SECRET_KEY'] = os.getenv('ADMIN_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads/pdfs'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Initialize E5 embedding model (SAME AS YOUR CHATBOT!)
print("📥 Loading E5 embedding model...")
embedding_model = SentenceTransformer("intfloat/multilingual-e5-large")
print("✅ E5 model loaded!")

# Initialize Pinecone
pinecone_client = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
PINECONE_INDEX = os.getenv('PINECONE_INDEX', 'shop-catalog')
index = pinecone_client.Index(PINECONE_INDEX)

# Admin users
ADMIN_USERS = {
    'admin@smartshop.com': {
        'password_hash': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'Admin User'
    }
}

# Documents metadata storage
DOCUMENTS_FILE = 'data/documents.json'

def load_documents():
    """Load documents metadata from file"""
    if os.path.exists(DOCUMENTS_FILE):
        with open(DOCUMENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_documents(documents):
    """Save documents metadata to file"""
    os.makedirs(os.path.dirname(DOCUMENTS_FILE), exist_ok=True)
    with open(DOCUMENTS_FILE, 'w') as f:
        json.dump(documents, f, indent=2)

# Authentication decorator
def require_admin(f):
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.admin_email = data['email']
            request.admin_role = data.get('role', 'user')
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


# ========================================
# AUTHENTICATION
# ========================================

@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    user = ADMIN_USERS.get(email)
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'email': email,
        'role': user['role'],
        'name': user['name'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {
            'email': email,
            'role': user['role'],
            'name': user['name']
        }
    })


@app.route('/admin/verify', methods=['GET'])
@require_admin
def verify_token():
    """Verify token is still valid"""
    return jsonify({
        'success': True,
        'email': request.admin_email,
        'role': request.admin_role
    })


# ========================================
# PDF PROCESSING WITH AUTO-EXTRACTION
# ========================================

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber (better than PyPDF2)"""
    try:
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        
        # Clean up the text - remove random spaces
        text = clean_extracted_text(text)
        
        return text.strip()
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def clean_extracted_text(text):

    """Clean up PDF text extraction issues while preserving URLs"""
    
    # 1. PROTECT URLs first (temporarily replace them)
    import re
    
    # Find all URLs and store them
    url_pattern = r'https?://[^\s\n]+'
    urls = re.findall(url_pattern, text)
    url_placeholders = {}
    
    for i, url in enumerate(urls):
        placeholder = f"__URL_PLACEHOLDER_{i}__"
        url_placeholders[placeholder] = url
        text = text.replace(url, placeholder)
    
    # 2. NOW do the cleaning (URLs are protected)
    
    # Remove spaces in middle of words (e.g., "AIRM AX" → "AIRMAX")
    text = re.sub(r'([A-Z])(\s+)([A-Z])', r'\1\3', text)
    
    # Fix broken words across lines (hyphen + newline)
    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)
    
    # Normalize multiple spaces to single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Fix common OCR errors in product names
    text = re.sub(r'AI R', 'AIR', text)
    text = re.sub(r'AIRM AX', 'AIRMAX', text)
    text = re.sub(r'Descrip\s+tion', 'Description', text)
    
    # 3. RESTORE URLs (put them back)
    for placeholder, url in url_placeholders.items():
        text = text.replace(placeholder, url)
    
    return text

def extract_products_from_text(text):
    """AUTO-EXTRACT structured product data from PDF"""
    products = []
    
    # FIRST: Fix broken URLs across lines
    text = re.sub(r'(https?://[^\s]*)-\s*\n\s*(\S+)', r'\1-\2', text)
    
    # Split by empty lines or separators
    sections = re.split(r'\n\s*\n+|---+', text)
    
    for section in sections:
        product = {}
        
        # Extract fields with regex (flexible matching)
        patterns = {
            'id': r'Id\s*:\s*([^\n]+)',
            'name': r'Name\s*:\s*([^\n]+)',
            'category': r'Category\s*:\s*([^\n]+)',
            'description': r'Description\s*:\s*([^\n]+)',
            'price': r'Price\s*:\s*(\d+)',
            'currency': r'Currency\s*:\s*([^\n]+)',
            'in_stock': r'In[_\s]*stock\s*:\s*(True|False|true|false)',
            'stock_quantity': r'Stock[_\s]*quantity\s*:\s*(\d+)',
            'image_url': r'Image[_\s]*url\s*:\s*(https?://\S+)',  # ← FIXED
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, section, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                
                # Type conversion
                if key in ['price', 'stock_quantity']:
                    product[key] = int(value)
                elif key == 'in_stock':
                    product[key] = value.lower() == 'true'
                else:
                    product[key] = value
        
        # Must have at least name and id to be valid
        if product.get('name') and product.get('id'):
            products.append(product)
            print(f"   📦 Extracted product: {product['name']} (ID: {product['id']})")
            if product.get('image_url'):
                print(f"       🖼️  Image URL: {product['image_url']}")  # ← DEBUG
    
    return products


def add_products_to_catalog(products, catalog_path='products/catalog.json'):
    """Add extracted products to catalog.json"""
    
    # Load existing catalog
    if os.path.exists(catalog_path):
        with open(catalog_path, 'r', encoding='utf-8') as f:
            catalog = json.load(f)
    else:
        catalog = []
    
    # Get existing IDs
    existing_ids = {p.get('id') for p in catalog}
    
    # Add new products
    added_count = 0
    for p in products:
        if p['id'] not in existing_ids:
            catalog_product = {
                "id": p['id'],
                "name": p['name'],
                "category": p.get('category', 'autres').lower(),
                "description": p.get('description', ''),
                "price": float(p.get('price', 0)),
                "currency": p.get('currency', 'FCFA'),
                "in_stock": p.get('in_stock', True),
                "stock_quantity": int(p.get('stock_quantity', 0)),
                "image_url": p.get('image_url', '')
            }
            catalog.append(catalog_product)
            added_count += 1
            print(f"   ✅ Added to catalog: {p['name']}")
        else:
            print(f"   ⚠️  Already exists (skipped): {p['name']}")
    
    # Save catalog
    if added_count > 0:
        os.makedirs(os.path.dirname(catalog_path), exist_ok=True)
        with open(catalog_path, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, ensure_ascii=False, indent=2)
        print(f"   💾 Catalog updated: +{added_count} products")
    
    return added_count


def run_catalog_ingestion():
    """Run ingestion_catalog.py to update Pinecone with new products"""
    try:
        print("   🔄 Running catalog ingestion...")
        result = subprocess.run(
            ['python', '-m','retrieval.ingest_catalog'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("   ✅ Catalog ingestion completed!")
            return True
        else:
            print(f"   ⚠️  Ingestion stderr: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("   ⚠️  Ingestion timeout (>120s)")
        return False
    except Exception as e:
        print(f"   ⚠️  Could not run ingestion: {e}")
        return False


def chunk_text(text, chunk_size=500, chunk_overlap=100):
    """Split text into chunks - Simple chunking without langchain"""
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence end
        if end < text_len:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:  # Only if break point is reasonable
                chunk = text[start:start + break_point + 1]
                end = start + break_point + 1
        
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk.strip())
        start = end - chunk_overlap  # Overlap for context
    
    return chunks


def generate_embeddings_e5(texts):
    """Generate embeddings using E5 model (SAME AS YOUR CHATBOT!)"""
    embeddings = []
    
    for text in texts:
        # Use PASSAGE prefix (same as your ingestion_catalog.py)
        prefixed_text = f"passage: {text}"
        embedding = embedding_model.encode(prefixed_text, normalize_embeddings=True).tolist()
        embeddings.append(embedding)
    
    return embeddings


def upload_to_pinecone(chunks, embeddings, metadata, extracted_products=None):
    """Upload vectors to Pinecone with enhanced metadata"""
    
    # Create product lookup from extracted products
    product_map = {}
    if extracted_products:
        for p in extracted_products:
            name_key = p['name'].lower().strip()
            product_map[name_key] = {
                'product_id': p.get('id'),
                'product_name': p['name'],
                'image_url': p.get('image_url'),
                'price': p.get('price'),
                'category': p.get('category')
            }
    
    vectors = []
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        vector_id = f"{metadata['document_id']}_chunk_{i}"
        
        # Try to match product in chunk text
        chunk_lower = chunk.lower()
        matched_product = None
        
        if product_map:
            for product_name, product_data in product_map.items():
                if product_name in chunk_lower:
                    matched_product = product_data
                    break
        
        # Build base metadata
        vec_metadata = {
            'document_id': metadata['document_id'],
            'filename': metadata['filename'],
            'document_type': metadata['document_type'],
            'chunk_index': i,
            'total_chunks': metadata['total_chunks'],
            'text': chunk[:1000],  # Limit text in metadata
            'uploaded_at': metadata['uploaded_at'],
            'uploaded_by': metadata['uploaded_by'],
            'type': 'pdf_document'  # Different from 'product' type
        }
        
        # Add product-specific metadata if matched
        if matched_product:
            vec_metadata.update({
                'product_id': matched_product['product_id'],
                'product_name': matched_product['product_name'],
                'image_url': matched_product['image_url'],
                'price': matched_product['price'],
                'category': matched_product['category']
            })
            print(f"   🔗 Chunk {i}: Linked to {matched_product['product_name']} (has image)")
        
        vectors.append({
            'id': vector_id,
            'values': embedding,
            'metadata': vec_metadata
        })
    
    # Upsert in batches
    batch_size = 100
    total_upserted = 0
    
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            print(f"   Upserting batch {i//batch_size + 1} ({len(batch)} vectors)...")
            
            # Upsert with explicit namespace
            result = index.upsert(vectors=batch, namespace='')
            
            print(f"   Upsert result: {result}")
            total_upserted += len(batch)
        except Exception as e:
            print(f"   ❌ Upsert error: {str(e)}")
            raise Exception(f"Failed to upload to Pinecone: {str(e)}")
    
    return total_upserted


# ========================================
# ADMIN ROUTES
# ========================================

@app.route('/admin/upload-pdf', methods=['POST'])
@require_admin
def upload_pdf():
    """Upload and process PDF with AUTO-EXTRACTION"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files allowed'}), 400
    
    try:
        # Generate document ID
        document_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        filename = secure_filename(file.filename)
        
        # Save file
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}_{filename}")
        file.save(filepath)
        
        # Extract text
        print(f"📄 Extracting text from {filename}...")
        text = extract_text_from_pdf(filepath)
        
        if not text.strip():
            os.remove(filepath)
            return jsonify({'error': 'No text found in PDF'}), 400
        
        # 🤖 AUTO-EXTRACT PRODUCTS
        print(f"🔍 Scanning PDF for products...")
        extracted_products = extract_products_from_text(text)
        
        catalog_updated = False
        added_count = 0
        
        if extracted_products:
            print(f"✅ Found {len(extracted_products)} product(s) in PDF")
            
            # Add to catalog
            added_count = add_products_to_catalog(extracted_products)
            
            # Run ingestion if products were added
            if added_count > 0:
                catalog_updated = run_catalog_ingestion()
        else:
            print(f"ℹ️  No structured product data found")
        
        # Chunk text
        print(f"✂️  Chunking text...")
        chunks = chunk_text(text)
        print(f"✅ Created {len(chunks)} chunks")
        
        # Generate E5 embeddings (SAME AS YOUR CHATBOT!)
        print(f"🧠 Generating E5 embeddings...")
        embeddings = generate_embeddings_e5(chunks)
        print(f"✅ Generated {len(embeddings)} embeddings")
        
        # Prepare metadata
        metadata = {
            'document_id': document_id,
            'filename': filename,
            'document_type': request.form.get('document_type', 'product_catalog'),
            'uploaded_by': request.admin_email,
            'uploaded_at': datetime.now().isoformat(),
            'total_chunks': len(chunks),
            'file_size': os.path.getsize(filepath)
        }
        
        # Upload to Pinecone (with product metadata)
        print(f"☁️  Uploading to Pinecone...")
        vector_count = upload_to_pinecone(chunks, embeddings, metadata, extracted_products)
        print(f"✅ Uploaded {vector_count} vectors")
        
        # Save document metadata
        documents = load_documents()
        documents.append({
            'document_id': document_id,
            'filename': filename,
            'document_type': metadata['document_type'],
            'uploaded_by': request.admin_email,
            'uploaded_at': metadata['uploaded_at'],
            'vector_count': vector_count,
            'file_size': metadata['file_size'],
            'chunk_count': len(chunks),
            'extracted_products': len(extracted_products),
            'added_to_catalog': added_count,
            'catalog_updated': catalog_updated
        })
        save_documents(documents)
        
        return jsonify({
            'success': True,
            'message': f'PDF processed with auto-extraction',
            'document': {
                'document_id': document_id,
                'filename': filename,
                'chunks': len(chunks),
                'vectors_uploaded': vector_count,
                'file_size': metadata['file_size'],
                'embedding_model': 'intfloat/multilingual-e5-large',
                'extracted_products': len(extracted_products),
                'added_to_catalog': added_count,
                'catalog_updated': catalog_updated,
                'products': [p['name'] for p in extracted_products] if extracted_products else []
            }
        })
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/documents', methods=['GET'])
@require_admin
def list_documents():
    """List all uploaded documents"""
    try:
        documents = load_documents()
        stats = index.describe_index_stats()
        
        return jsonify({
            'success': True,
            'documents': documents,
            'stats': {
                'total_vectors': stats.get('total_vector_count', 0),
                'total_documents': len(documents)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/document/<document_id>', methods=['DELETE'])
@require_admin
def delete_document(document_id):
    """Delete document from Pinecone"""
    try:
        print(f"🗑️  Deleting document {document_id}...")
        
        # Delete from Pinecone
        index.delete(filter={'document_id': document_id})
        
        # Remove from metadata
        documents = load_documents()
        documents = [d for d in documents if d['document_id'] != document_id]
        save_documents(documents)
        
        # Delete file
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith(document_id):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.remove(filepath)
        
        return jsonify({
            'success': True,
            'message': f'Document {document_id} deleted'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/search-test', methods=['POST'])
@require_admin
def search_test():
    """Test search using E5 embeddings"""
    data = request.json
    query = data.get('query', '')
    top_k = data.get('top_k', 5)
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    try:
        print(f"🔍 Searching with E5: {query}")
        
        # Generate query embedding with E5 (use "query:" prefix)
        query_text = f"query: {query}"
        query_embedding = embedding_model.encode(query_text, normalize_embeddings=True).tolist()
        
        # Search Pinecone
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        # Format results
        formatted_results = []
        for match in results.get('matches', []):
            formatted_results.append({
                'score': round(match['score'], 4),
                'text': match['metadata'].get('text', '')[:200] + '...',
                'document_id': match['metadata'].get('document_id', ''),
                'filename': match['metadata'].get('filename', ''),
                'chunk_index': match['metadata'].get('chunk_index', 0),
                'type': match['metadata'].get('type', 'unknown'),
                'product_name': match['metadata'].get('product_name'),
                'image_url': match['metadata'].get('image_url')
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results),
            'embedding_model': 'E5'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/stats', methods=['GET'])
@require_admin
def get_stats():
    """Get admin statistics"""
    try:
        stats = index.describe_index_stats()
        documents = load_documents()
        
        total_size = sum(doc.get('file_size', 0) for doc in documents)
        total_products = sum(doc.get('extracted_products', 0) for doc in documents)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_vectors': stats.get('total_vector_count', 0),
                'total_documents': len(documents),
                'total_products_extracted': total_products,
                'total_storage_bytes': total_size,
                'total_storage_mb': round(total_size / (1024 * 1024), 2),
                'index_fullness': stats.get('index_fullness', 0),
                'dimensions': stats.get('dimension', 1024),
                'embedding_model': 'intfloat/multilingual-e5-large'
            },
            'recent_uploads': documents[-5:][::-1] if documents else []
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'embedding_model': 'intfloat/multilingual-e5-large',
        'pinecone_index': PINECONE_INDEX,
        'features': ['auto-extraction', 'catalog-integration', 'pdfplumber', 'e5']
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🤖 SmartShop Admin - AUTO-EXTRACTION ENABLED")
    print("=" * 70)
    print(f"📡 API URL: http://localhost:5003")
    print(f"🗄️  Pinecone Index: {PINECONE_INDEX}")
    print(f"🧠 Embedding Model: intfloat/multilingual-e5-large")
    print(f"📄 PDF Tool: pdfplumber (with text cleaning)")
    print(f"📁 Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print()
    print("✨ AUTO-EXTRACTION FEATURES:")
    print("  ✅ Auto-detects products in PDFs")
    print("  ✅ Auto-adds to catalog.json")
    print("  ✅ Auto-runs ingestion_catalog.py")
    print("  ✅ Links images to PDF chunks")
    print("  ✅ Images work automatically in chatbot!")
    print()
    print("Default Admin Credentials:")
    print("  Email: admin@smartshop.com")
    print("  Password: admin123")
    print()
    print("⚠️  CHANGE PASSWORD IN PRODUCTION!")
    print("=" * 70)
    
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('data', exist_ok=True)
    os.makedirs('catalog', exist_ok=True)
    
    app.run(
        host='0.0.0.0',
        port=5003,
        debug=True
    )
