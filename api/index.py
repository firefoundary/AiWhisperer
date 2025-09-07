from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import markdown
import os

app = Flask(__name__, template_folder='../frontend')
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.5-flash')

@app.route('/api/create_prompt_chain', methods=['POST'])
def optimize():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    system_prompt = f"""
You are an expert prompt engineer who creates detailed, professional prompt templates.

When given a user request, generate a comprehensive prompt template with clear structure and formatting.

User request: "{user_input}"

Generate a detailed prompt template:
"""
    
    try:
        response = model.generate_content(system_prompt)
        raw_text = response.text.strip()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(raw_text)
        
        return jsonify({
            'user_input': user_input,
            'steps': [{
                'step_number': 1,
                'output': raw_text,  # Plain text for copying
                'html_output': html_content,  # HTML for display
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
