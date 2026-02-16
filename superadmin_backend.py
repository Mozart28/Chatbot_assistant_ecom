"""
Super Admin Backend - LLM Model Management
Mistral AI + Groq + Hugging Face Llama
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import jwt
import os
from datetime import datetime, timedelta
import json

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/superadmin/*": {"origins": "*"}})

app.config['SECRET_KEY'] = os.getenv('SUPERADMIN_SECRET_KEY', 'super-secret-key-change-in-production')

# Super Admin credentials
SUPERADMIN_USERS = {
    'superadmin@smartshop.com': {
        'password_hash': generate_password_hash('superadmin123'),
        'role': 'superadmin'
    }
}

# YOUR 3 LLM PROVIDERS
AVAILABLE_MODELS = {
    'mistral': {
        'mistral-tiny': {
            'name': 'Mistral Tiny',
            'provider': 'Mistral AI',
            'cost_per_1m_tokens': 0.14,
            'speed': 'very_fast',
            'quality': 'good',
            'description': 'Le plus rapide et économique'
        },
        'open-mistral-7b': {
            'name': 'Mistral 7B',
            'provider': 'Mistral AI',
            'cost_per_1m_tokens': 0.25,
            'speed': 'fast',
            'quality': 'very_good',
            'description': 'Excellent rapport qualité/prix'
        },
        'mistral-small-latest': {
            'name': 'Mistral Small',
            'provider': 'Mistral AI',
            'cost_per_1m_tokens': 2.0,
            'speed': 'medium',
            'quality': 'excellent',
            'description': 'Haute qualité, usage actuel'
        },
        'mistral-large-latest': {
            'name': 'Mistral Large',
            'provider': 'Mistral AI',
            'cost_per_1m_tokens': 8.0,
            'speed': 'medium',
            'quality': 'outstanding',
            'description': 'Meilleure qualité Mistral'
        }
    },
    'groq': {
        'llama-3.1-70b-versatile': {
            'name': 'Llama 3.1 70B (Groq)',
            'provider': 'Groq',
            'cost_per_1m_tokens': 0.59,
            'speed': 'ultra_fast',
            'quality': 'excellent',
            'description': 'Ultra-rapide grâce à Groq LPU'
        },
        'llama-3.1-8b-instant': {
            'name': 'Llama 3.1 8B (Groq)',
            'provider': 'Groq',
            'cost_per_1m_tokens': 0.05,
            'speed': 'ultra_fast',
            'quality': 'very_good',
            'description': 'Le plus rapide et économique'
        },
        'llama-3.3-70b-versatile': {
            'name': 'Llama 3.3 70B (Groq)',
            'provider': 'Groq',
            'cost_per_1m_tokens': 0.59,
            'speed': 'ultra_fast',
            'quality': 'outstanding',
            'description': 'Dernière version Llama sur Groq'
        },
        'mixtral-8x7b-32768': {
            'name': 'Mixtral 8x7B (Groq)',
            'provider': 'Groq',
            'cost_per_1m_tokens': 0.24,
            'speed': 'ultra_fast',
            'quality': 'excellent',
            'description': 'Mixtral ultra-rapide'
        }
    },
    'huggingface': {
        'meta-llama/Llama-3.2-3B-Instruct': {
            'name': 'Llama 3.2 3B',
            'provider': 'Hugging Face',
            'cost_per_1m_tokens': 0.00,  # Gratuit en self-hosted
            'speed': 'fast',
            'quality': 'good',
            'description': 'Gratuit, léger, auto-hébergé'
        },
        'meta-llama/Llama-3.1-8B-Instruct': {
            'name': 'Llama 3.1 8B',
            'provider': 'Hugging Face',
            'cost_per_1m_tokens': 0.00,
            'speed': 'medium',
            'quality': 'very_good',
            'description': 'Gratuit, bonne qualité'
        }
    }
}

CONFIG_FILE = 'data/model_config.json'
USAGE_FILE = 'data/usage_stats.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        'current_provider': 'mistral',
        'current_model': 'mistral-small-latest',
        'auto_switch_enabled': False,
        'monthly_budget': 100.0,
        'fallback_model': 'open-mistral-7b'
    }

def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_usage_stats():
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
    return {
        'total_tokens': 0,
        'total_cost': 0.0,
        'requests_count': 0,
        'by_model': {},
        'by_date': {},
        'last_reset': datetime.now().isoformat()
    }

def save_usage_stats(stats):
    os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
    with open(USAGE_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def log_usage(model, tokens, cost):
    stats = load_usage_stats()
    stats['total_tokens'] += tokens
    stats['total_cost'] += cost
    stats['requests_count'] += 1
    
    if model not in stats['by_model']:
        stats['by_model'][model] = {'tokens': 0, 'cost': 0, 'requests': 0}
    stats['by_model'][model]['tokens'] += tokens
    stats['by_model'][model]['cost'] += cost
    stats['by_model'][model]['requests'] += 1
    
    today = datetime.now().strftime('%Y-%m-%d')
    if today not in stats['by_date']:
        stats['by_date'][today] = {'tokens': 0, 'cost': 0, 'requests': 0}
    stats['by_date'][today]['tokens'] += tokens
    stats['by_date'][today]['cost'] += cost
    stats['by_date'][today]['requests'] += 1
    
    save_usage_stats(stats)

def require_superadmin(f):
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            if data.get('role') != 'superadmin':
                return jsonify({'error': 'Superadmin access required'}), 403
            request.superadmin_email = data['email']
        except:
            return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# ========================================
# AUTHENTICATION
# ========================================

@app.route('/superadmin/login', methods=['POST'])
def superadmin_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = SUPERADMIN_USERS.get(email)
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    token = jwt.encode({
        'email': email,
        'role': 'superadmin',
        'exp': datetime.utcnow() + timedelta(days=7)  # 7 days
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'token': token,
        'user': {'email': email, 'role': 'superadmin'}
    })

# ========================================
# MODEL MANAGEMENT
# ========================================

@app.route('/superadmin/models', methods=['GET'])
@require_superadmin
def get_available_models():
    return jsonify({
        'success': True,
        'models': AVAILABLE_MODELS
    })

@app.route('/superadmin/config', methods=['GET'])
@require_superadmin
def get_config():
    config = load_config()
    stats = load_usage_stats()
    
    return jsonify({
        'success': True,
        'config': config,
        'current_model_info': AVAILABLE_MODELS.get(
            config['current_provider'], {}
        ).get(config['current_model'], {}),
        'usage_summary': {
            'total_tokens': stats['total_tokens'],
            'total_cost': round(stats['total_cost'], 2),
            'requests_count': stats['requests_count']
        }
    })

@app.route('/superadmin/switch-model', methods=['POST'])
@require_superadmin
def switch_model():
    data = request.json
    provider = data.get('provider')
    model = data.get('model')
    
    if provider not in AVAILABLE_MODELS:
        return jsonify({'error': f'Provider inconnu: {provider}'}), 400
    
    if model not in AVAILABLE_MODELS[provider]:
        return jsonify({'error': f'Modèle inconnu: {model}'}), 400
    
    config = load_config()
    config['current_provider'] = provider
    config['current_model'] = model
    save_config(config)
    
    update_agent_model(provider, model)
    
    return jsonify({
        'success': True,
        'message': f'Switched to {AVAILABLE_MODELS[provider][model]["name"]}',
        'config': config
    })

@app.route('/superadmin/config/update', methods=['POST'])
@require_superadmin
def update_config():
    data = request.json
    config = load_config()
    
    if 'auto_switch_enabled' in data:
        config['auto_switch_enabled'] = data['auto_switch_enabled']
    if 'monthly_budget' in data:
        config['monthly_budget'] = float(data['monthly_budget'])
    if 'fallback_model' in data:
        config['fallback_model'] = data['fallback_model']
    
    save_config(config)
    return jsonify({'success': True, 'config': config})

# ========================================
# USAGE MONITORING
# ========================================

@app.route('/superadmin/usage', methods=['GET'])
@require_superadmin
def get_usage():
    stats = load_usage_stats()
    config = load_config()
    
    budget_used_percent = (stats['total_cost'] / config['monthly_budget']) * 100 if config['monthly_budget'] > 0 else 0
    
    return jsonify({
        'success': True,
        'stats': stats,
        'budget': {
            'monthly_limit': config['monthly_budget'],
            'used': round(stats['total_cost'], 2),
            'remaining': round(config['monthly_budget'] - stats['total_cost'], 2),
            'percent_used': round(budget_used_percent, 1)
        }
    })

@app.route('/superadmin/usage/reset', methods=['POST'])
@require_superadmin
def reset_usage():
    stats = {
        'total_tokens': 0,
        'total_cost': 0.0,
        'requests_count': 0,
        'by_model': {},
        'by_date': {},
        'last_reset': datetime.now().isoformat()
    }
    save_usage_stats(stats)
    return jsonify({'success': True, 'message': 'Usage statistics reset'})

@app.route('/superadmin/usage/log', methods=['POST'])
def log_usage_endpoint():
    data = request.json
    model = data.get('model')
    tokens = data.get('tokens', 0)
    cost = data.get('cost', 0.0)
    log_usage(model, tokens, cost)
    return jsonify({'success': True})

# ========================================
# HELPER FUNCTIONS
# ========================================

def update_agent_model(provider, model):
    """Update agent's model configuration"""
    os.environ['CURRENT_LLM_PROVIDER'] = provider
    os.environ['CURRENT_LLM_MODEL'] = model
    
    agent_config = {
        'provider': provider,
        'model': model,
        'updated_at': datetime.now().isoformat()
    }
    
    os.makedirs('config', exist_ok=True)
    with open('config/llm_config.json', 'w') as f:
        json.dump(agent_config, f, indent=2)
    
    print(f"✅ Switched to {provider}/{model}")

@app.route('/superadmin/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("=" * 70)
    print("🔐 SmartShop Super Admin - LLM Management")
    print("=" * 70)
    print(f"📡 API: http://localhost:5004")
    print()
    print("🎯 Available Providers:")
    print("  1. Mistral AI (4 models)")
    print("  2. Groq (4 models - Ultra-fast!)")
    print("  3. Hugging Face (2 models - Gratuit!)")
    print()
    print("Login: superadmin@smartshop.com / superadmin123")
    print("=" * 70)
    
    os.makedirs('data', exist_ok=True)
    os.makedirs('config', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5004, debug=True)
