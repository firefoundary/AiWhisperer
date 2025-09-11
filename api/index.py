from flask import Flask, request, jsonify, send_from_directory
from supabase import create_client
import google.generativeai as genai
import os
from datetime import datetime

# Initialize Flask app with frontend configuration
app = Flask(__name__, 
            static_folder='../frontend', 
            static_url_path='')

# Initialize services
supabase = create_client(
    os.environ.get('PROJ_SUPA_URL'), 
    os.environ.get('SUPA_ANON_API')
)
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# FRONTEND ROUTES - Serve your AI Whisperer interface
@app.route('/')
def home():
    """Serve the main AI Whisperer interface"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/templates')
def templates():
    """Serve the templates page"""
    return send_from_directory(app.static_folder, 'templates.html')

# Catch-all route for single-page application
@app.route('/<path:path>')
def catch_all(path):
    """Serve static files or default to index.html for SPA routing"""
    try:
        # Try to serve the requested file
        return send_from_directory(app.static_folder, path)
    except:
        # If file doesn't exist, serve index.html (for SPA routing)
        return send_from_directory(app.static_folder, 'index.html')

# API ROUTES - Your existing enhanced functionality
@app.route('/api/enhanced_prompt_generation', methods=['POST'])
def enhanced_generation():
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    if not user_input:
        return jsonify({'error': 'Empty input provided', 'success': False}), 400
    
    try:
        # Step 1: Generate embedding for user input
        embedding_result = genai.embed_content(
            model="models/text-embedding-004",
            content=user_input,
            task_type="retrieval_query"
        )
        
        # Step 2: Find similar prompts using vector search
        similar_prompts = supabase.rpc('match_prompts', {
            'query_embedding': embedding_result['embedding'],
            'match_threshold': 0.45,
            'match_count': 3
        }).execute()
        
        # Step 3: Build context-aware prompt
        context = format_retrieved_context(similar_prompts.data)
        enhanced_prompt = create_enhanced_system_prompt(user_input, context)
        
        # Step 4: Generate final response with Gemini
        final_response = genai.GenerativeModel('gemini-2.5-flash').generate_content(enhanced_prompt)
        
        # Step 5: Log analytics
        context_quality = calculate_context_quality(similar_prompts.data)
        log_prompt_generation(user_input, len(similar_prompts.data), context_quality, True)
        
        return jsonify({
            'user_input': user_input,
            'similar_prompts_used': len(similar_prompts.data),
            'generated_template': final_response.text,
            'context_quality': context_quality,
            'success': True
        })
        
    except Exception as e:
        log_prompt_generation(user_input, 0, 0.0, False)
        return jsonify({
            'user_input': user_input,
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/create_prompt_chain', methods=['POST'])
def create_prompt_chain():
    """Fallback API for simple generation"""
    data = request.get_json()
    user_input = data.get('user_input', '').strip()
    
    if not user_input:
        return jsonify({'error': 'Empty input provided', 'success': False}), 400
    
    try:
        system_prompt = f"""You are a skilled professional with over 10 years of experience creating effective AI interactions.

Your task is to create a comprehensive, ready-to-use prompt template based on: "{user_input}"

Generate a detailed prompt template with fill-in-the-blank sections using underscores."""

        response = genai.GenerativeModel('gemini-2.5-flash').generate_content(system_prompt)
        
        return jsonify({
            'user_input': user_input,
            'steps': [{
                'step_number': 1,
                'output': response.text,
                'success': True
            }],
            'success': True
        })
        
    except Exception as e:
        return jsonify({
            'user_input': user_input,
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

# HELPER FUNCTIONS (Your existing functions)
def format_retrieved_context(similar_prompts):
    """Format retrieved prompts as rich context"""
    if not similar_prompts:
        return "No similar examples found in database."
    
    context_parts = []
    for i, prompt in enumerate(similar_prompts, 1):
        context_parts.append(f"""
EXAMPLE {i} (Similarity: {prompt['similarity']:.2f}):
Task: {prompt['task_description']}
Effective Approach: {prompt['good_prompt'][:400]}...
Category: {prompt.get('prompt_type', 'General')}
        """)
    
    return "\n".join(context_parts)

def create_enhanced_system_prompt(user_input, context):
    """Create the intelligent system prompt"""
    return f"""You are an expert prompt engineer with 10+ years of experience creating highly effective AI interactions.

RELEVANT EXAMPLES FROM KNOWLEDGE BASE:
{context}

USER'S REQUEST: "{user_input}"

TASK: Create a comprehensive, professional prompt template that incorporates lessons from the similar examples above.

Generate the optimized prompt template now:"""

def calculate_context_quality(prompts):
    """Assess quality of retrieved context"""
    if not prompts:
        return 0.0
    
    avg_similarity = sum(p['similarity'] for p in prompts) / len(prompts)
    return round(avg_similarity, 3)

def log_prompt_generation(user_input, similar_prompts_count, context_quality, success):
    """Log usage for analytics"""
    try:
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input_length': len(user_input),
            'similar_prompts_used': similar_prompts_count,
            'context_quality': context_quality,
            'success': success
        }
        supabase.table('usage_analytics').insert(log_entry).execute()
    except:
        pass  # Don't fail if logging fails

# Required for Railway
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
