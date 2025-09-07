from flask import Flask, send_from_directory
from pathlib import Path

app = Flask(__name__)
frontend_dir = Path(__file__).parent.parent / 'frontend'

@app.route('/')
def serve_index():
    return send_from_directory(frontend_dir, 'index.html')

@app.route('/templates.html')
def serve_templates():
    return send_from_directory(frontend_dir, 'templates.html')

@app.route('/<path:path>')
def serve_static(path):
    # Serve other static files if needed
    return send_from_directory(frontend_dir, path)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
