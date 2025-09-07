from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/templates')
def templates():
    return render_template('templates.html')

@app.route('/api/create_prompt_chain', methods=['POST'])
def optimize():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    system_prompt = f"""You are an expert prompt engineer who creates detailed, professional prompt templates.

When given a user request, generate a comprehensive prompt template using PLAIN TEXT only (no markdown, no bold formatting, no asterisks).

User request: "{user_input}"

Generate a detailed plain text prompt template:"""
    
    try:
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip()
        
        return jsonify({
            'user_input': user_input,
            'steps': [{
                'step_number': 1,
                'output': raw_text,
                'success': True
            }]
        })
        
    except Exception as e:
        return jsonify({
            'user_input': user_input,
            'steps': [{
                'step_number': 1,
                'output': f"Error generating prompt: {str(e)}",
                'success': False
            }]
        })

@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({"status": "AI Whisperer API is working"})

if __name__ == '__main__':
    app.run(debug=True)
