from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

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
    
    system_prompt = f"""You are a skilled professional with over 10 years of experience in your field. Your expertise lies in understanding client needs and translating them into actionable project plans.

    Your task is to create a comprehensive, ready-to-use prompt template based on the user's request. The template should include fill-in-the-blank sections using underscores (like "Purpose: __________") where specific details need to be provided.

    User request: "{user_input}"

    Generate a detailed prompt template that follows this structure:

    **Opening:** Start with "You are a skilled [profession] with over 10 years of experience..."
    **Task Statement:** "Your task is to assist in creating [project type]..."
    **Fill-in Details:** Use underscores for blanks (e.g., "Project Purpose: __________")
    **Guidelines Section:** Include specific requirements and structure
    **Examples Section:** Provide concrete examples of what to include
    **Cautions Section:** List important considerations and best practices
    **Closing:** End with the desired outcome

    Format the output as a complete, ready-to-use prompt template with clear sections separated by "---" dividers.

    Example format:
    You are a skilled [profession] with over 10 years of experience...
    Your task is to assist in creating [project]. Here are the details I need to provide:
    - [Detail 1]: __________
    - [Detail 2]: __________
    ---
    [Guidelines and structure]
    ---
    [Examples section]
    ---
    [Cautions section]
    ---
    [Final outcome description]

    Generate the complete template now:"""

    
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
