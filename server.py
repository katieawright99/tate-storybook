from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv() # load ANTHROPIC_API_KEY from .env

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app) # allow browser during development

API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    print("Warning: ANTHROPIC_API_KEY not set in .env")

# Serve index and static files
@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'tate-storybook.html')

@app.route('/<path:filename>', methods=['GET'])
def static_files(filename):
    return send_from_directory('.', filename)

# Proxy endpoint: client -> this server -> Anthropic
@app.route('/api/messages', methods=['POST'])
def proxy_messages():
    try:
        payload = request.get_json(force=True)
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': API_KEY,
            'anthropic-version': '2023-06-01'
        }
        resp = requests.post('https://api.anthropic.com/v1/messages', json=payload, headers=headers, timeout=30)
        return (resp.content, resp.status_code, {'Content-Type': resp.headers.get('Content-Type', 'application/json')})
    except requests.exceptions.RequestException as e:
        print("Error contacting Anthropic:", e)
        return jsonify({'error': 'Server error contacting Anthropic'}), 500
    except Exception as e:
        print("Server error:", e)
        return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)), debug=False)
