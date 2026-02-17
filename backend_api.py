"""
Backend API for SmartShop React Frontend
This connects your existing Streamlit agent logic to the React frontend via REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add your existing project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your existing components
from core.agent import CommercialAgent


from core.state_manager import ConversationState
from tools.cart import add_product_to_cart
from tools.contact import request_contact

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Store conversations in memory (use Redis/DB in production)
conversations = {}

def get_or_create_conversation(conversation_id=None):
    """Get existing conversation or create new one"""
    if conversation_id and conversation_id in conversations:
        return conversations[conversation_id]
    
    # Create new conversation
    new_id = conversation_id or f"conv_{len(conversations)}"
    state = ConversationState()
    agent = CommercialAgent(state=state)
    
    conversations[new_id] = {
        'agent': agent,
        'state': state,
        'cart': []
    }
    
    return conversations[new_id]


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint - processes user messages"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get conversation
        conv = get_or_create_conversation(conversation_id)
        agent = conv['agent']
        state = conv['state']
        
        # Process message through your agent
        response = agent.run(user_message)
        
        # Format response for React frontend
        result = format_response(response, conv)
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            'error': str(e),
            'message': 'Désolé, une erreur s\'est produite.'
        }), 500


def format_response(agent_response, conv):
    """Convert agent response to React-friendly format"""
    
    if isinstance(agent_response, dict):
        response_type = agent_response.get('type', 'text')
        
        # Text response
        if response_type == 'text':
            return {
                'type': 'text',
                'message': agent_response.get('message', ''),
                'conversation_id': list(conversations.keys())[list(conversations.values()).index(conv)],
                'pending_choice': agent_response.get('pending_choice')
            }
        
        # Product image display
        elif response_type == 'product_image':
            product = agent_response.get('product', {})
            return {
                'type': 'product_image',
                'message': f"🖼️ {product.get('name', 'Produit')}",
                'product': {
                    'id': product.get('id'),
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'image_url': product.get('image_url'),
                    'in_stock': product.get('in_stock', True)
                },
                'conversation_id': list(conversations.keys())[list(conversations.values()).index(conv)]
            }
        
        # Add to cart
        elif response_type == 'add_to_cart':
            product = agent_response.get('product', {})
            
            # Add to conversation cart
            conv['cart'].append(product)
            
            return {
                'type': 'cart_updated',
                'message': f"✅ {product.get('name')} ajouté au panier !",
                'cart': conv['cart'],
                'conversation_id': list(conversations.keys())[list(conversations.values()).index(conv)]
            }
        
        # Contact agent
        elif response_type == 'request_contact':
            contact_info = request_contact()
            return {
                'type': 'contact_agent',
                'message': contact_info,
                'conversation_id': list(conversations.keys())[list(conversations.values()).index(conv)]
            }
    
    # Fallback for string responses
    return {
        'type': 'text',
        'message': str(agent_response),
        'conversation_id': list(conversations.keys())[list(conversations.values()).index(conv)]
    }


@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get cart contents"""
    try:
        conversation_id = request.args.get('conversation_id')
        conv = get_or_create_conversation(conversation_id)
        
        return jsonify({
            'cart': conv['cart'],
            'total': sum(int(item.get('price', 0)) for item in conv['cart'])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        product = data.get('product')
        
        conv = get_or_create_conversation(conversation_id)
        conv['cart'].append(product)
        
        return jsonify({
            'success': True,
            'message': 'Produit ajouté',
            'cart': conv['cart']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    """Clear cart"""
    try:
        conversation_id = request.args.get('conversation_id')
        conv = get_or_create_conversation(conversation_id)
        conv['cart'] = []
        
        return jsonify({'success': True, 'message': 'Panier vidé'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/conversation/reset', methods=['POST'])
def reset_conversation():
    """Start new conversation"""
    try:
        data = request.json
        old_id = data.get('conversation_id')
        
        # Create new conversation
        new_conv = get_or_create_conversation()
        new_id = list(conversations.keys())[list(conversations.values()).index(new_conv)]
        
        # Delete old conversation
        if old_id and old_id in conversations:
            del conversations[old_id]
        
        return jsonify({
            'success': True,
            'conversation_id': new_id,
            'message': 'Nouvelle conversation créée'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit rating/feedback"""
    try:
        data = request.json
        rating = data.get('rating')
        message_index = data.get('message_index')
        
        # Save to your existing feedback database
        # (reuse your save_rating function from Streamlit app)
        
        return jsonify({
            'success': True,
            'message': 'Merci pour votre retour !'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'active_conversations': len(conversations)
    })


if __name__ == '__main__':
    print("🚀 SmartShop Backend API starting...")
    print("📡 Frontend should connect to: http://localhost:5002")
    print("🔧 CORS enabled for React frontend")
    print("")
    port = int(os.environ.get("PORT", 5002))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )

