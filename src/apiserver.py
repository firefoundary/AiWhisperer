from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

# Import AIWhisperer and Config
from ai_whisperer import AIWhisperer, Config

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for frontend-backend communication

# Initialize AI Whisperer
try:
    config = Config()
    optimizer = AIWhisperer(config)
    print("✅ AI Whisperer Prompt Optimizer initialized successfully")
except Exception as e:
    print(f"❌ Error initializing AI Whisperer: {e}")
    optimizer = None

# API endpoint to optimize prompts
@app.route('/api/create_prompt_chain', methods=['POST'])
def optimize_prompt():
    if not optimizer:
        return jsonify({"error": "AI Whisperer not initialized"}), 500
    
    try:
        data = request.get_json(force=True)
        user_input = data.get('user_input', '').strip()
        
        if not user_input:
            return jsonify({"error": "Missing user_input"}), 400
        
        print(f"🔄 Optimizing prompt: {user_input}")
        results = optimizer.execute_prompt_chain(user_input)
        print("✅ Prompt optimized successfully")
        
        return jsonify(results)
    
    except Exception as e:
        print(f"❌ Error optimizing prompt: {e}")
        return jsonify({"error": str(e)}), 500

# Test endpoint
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"status": "Prompt Optimizer API is working", "message": "Backend connected"})

# Serve frontend files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/templates')
@app.route('/templates.html')
def serve_templates():
    return send_from_directory(app.static_folder, 'templates.html')

# Serve static files (CSS, JS, images)
@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    print("🚀 Starting AI Whisperer Prompt Optimizer Server...")
    app.run(host='0.0.0.0', port=8000, debug=True)
