from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

app = Flask(__name__, template_folder='../frontend')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/api/create_prompt_chain', methods=['POST'])
def optimize():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    prompt = f"Optimize this request into a detailed, effective AI prompt: '{user_input}'"
    response = model.generate_content(prompt)
    
    return jsonify({
        'user_input': user_input,
        'steps': [{'step_number': 1, 'output': response.text.strip(), 'success': True}]
    })
