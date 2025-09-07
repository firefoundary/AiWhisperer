from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
current_dir = Path(__file__).parent  
project_root = current_dir.parent    
src_dir = project_root / 'src'      
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
try:
    from ai_whisperer import AIWhisperer
    from config import Config
    print("✅ Successfully imported AI Whisperer classes")
except ImportError as e:
    print(f"❌ Import error: {e}")
    AIWhisperer = None
    Config = None
app = Flask(__name__, 
            template_folder='../frontend',
            static_folder='../frontend')
CORS(app)

# Initialize AI Whisperer
whisperer = None
if AIWhisperer and Config:
    try:
        config = Config()
        whisperer = AIWhisperer(config)
        print("✅ AI Whisperer initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing AI Whisperer: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/api/create_prompt_chain', methods=['POST'])
def create_prompt_chain():
    if not whisperer:
        return jsonify({"error": "AI Whisperer not initialized"}), 500
    
    try:
        data = request.get_json()
        user_input = data.get('user_input', '').strip()
        
        if not user_input:
            return jsonify({"error": "Missing user_input"}), 400
        
        print(f"🔄 Processing request: {user_input}")
        results = whisperer.execute_prompt_chain(user_input)
        print("✅ Request processed successfully")
        
        return jsonify(results)
    
    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"status": "AI Whisperer API is working", "message": "Backend connected"})

# This is required for Vercel
if __name__ == '__main__':
    app.run(debug=True)
