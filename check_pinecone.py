"""
Check what's in Pinecone - Debug Script
"""
from pinecone import Pinecone
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index_name = os.getenv('PINECONE_INDEX', 'shop-catalog')

print(f"🔍 Inspecting Pinecone Index: {index_name}")
print("=" * 60)

try:
    index = pc.Index(index_name)
    
    # Get index stats
    stats = index.describe_index_stats()
    
    print(f"\n📊 INDEX STATISTICS:")
    print(f"   Total Vectors: {stats.get('total_vector_count', 0)}")
    print(f"   Dimension: {stats.get('dimension', 0)}")
    print(f"   Index Fullness: {stats.get('index_fullness', 0) * 100:.2f}%")
    
    # Check namespaces
    namespaces = stats.get('namespaces', {})
    print(f"\n📁 NAMESPACES:")
    if namespaces:
        for ns, ns_stats in namespaces.items():
            print(f"   {ns}: {ns_stats.get('vector_count', 0)} vectors")
    else:
        print("   Default namespace (no named namespaces)")
    
    # Try to fetch some vectors by querying with a dummy vector
    print(f"\n🔎 SAMPLE VECTORS (first 10):")
    
    # Create a dummy query vector (all zeros)
    dimension = stats.get('dimension', 1024)
    dummy_vector = [0.0] * dimension
    
    # Query to get any vectors
    results = index.query(
        vector=dummy_vector,
        top_k=10,
        include_metadata=True
    )
    
    if results.get('matches'):
        print(f"\n✅ Found {len(results['matches'])} sample vectors:\n")
        
        for i, match in enumerate(results['matches'], 1):
            metadata = match.get('metadata', {})
            print(f"{i}. ID: {match['id']}")
            print(f"   Type: {metadata.get('type', 'unknown')}")
            
            # Check if it's a product
            if metadata.get('type') == 'product':
                print(f"   Name: {metadata.get('name', 'N/A')}")
                print(f"   Category: {metadata.get('category', 'N/A')}")
                print(f"   Price: {metadata.get('price', 'N/A')} {metadata.get('currency', '')}")
            
            # Check if it's a PDF document
            elif metadata.get('type') == 'pdf_document':
                print(f"   Filename: {metadata.get('filename', 'N/A')}")
                print(f"   Document ID: {metadata.get('document_id', 'N/A')}")
                print(f"   Chunk: {metadata.get('chunk_index', 0)}/{metadata.get('total_chunks', 0)}")
                print(f"   Text preview: {metadata.get('text', '')[:100]}...")
            
            else:
                print(f"   Metadata: {metadata}")
            
            print()
    else:
        print("   ❌ No vectors found in index!")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    total = stats.get('total_vector_count', 0)
    
    # Count by type
    product_count = 0
    pdf_count = 0
    
    for match in results.get('matches', []):
        meta_type = match.get('metadata', {}).get('type')
        if meta_type == 'product':
            product_count += 1
        elif meta_type == 'pdf_document':
            pdf_count += 1
    
    print(f"   Total vectors: {total}")
    print(f"   Sample breakdown:")
    print(f"     - Products: {product_count} (in sample)")
    print(f"     - PDF docs: {pdf_count} (in sample)")
    print(f"     - Other: {10 - product_count - pdf_count} (in sample)")
    
    print("\n✅ Inspection complete!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nMake sure:")
    print("  1. PINECONE_API_KEY is set in .env")
    print("  2. PINECONE_INDEX name is correct")
    print("  3. Index exists in Pinecone")
