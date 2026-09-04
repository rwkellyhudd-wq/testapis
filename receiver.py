from quart import Quart, jsonify, request
import json
from datetime import datetime

app = Quart(__name__)

@app.route('/token', methods=['POST'])
async def receive_token():
    try:
        data = await request.json
        token = data.get('token')
        url = data.get('url')
        
        # Token'ı dosyaya kaydet
        with open('tokens.txt', 'a') as f:
            f.write(f"[{datetime.now()}] {token}\n")
        
        # JSON olarak da kaydet
        with open('tokens_log.json', 'a') as f:
            f.write(json.dumps(data) + '\n')
        
        return jsonify({'status': 'success', 'message': 'Token received'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/tokens', methods=['GET'])
async def get_tokens():
    try:
        with open('tokens.txt', 'r') as f:
            tokens = f.read().split('\n')
        return jsonify({'tokens': tokens[-100:]})  # Son 100 token
    except:
        return jsonify({'tokens': []})

@app.route('/', methods=['GET'])
async def home():
    return jsonify({
        'service': 'Token Receiver',
        'endpoints': {
            'POST /token': 'Receive token',
            'GET /tokens': 'View tokens'
        }
    })
