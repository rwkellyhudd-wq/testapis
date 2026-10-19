# Render'da çalışacak kod (Köprü) - Görünür mod zorunlu
from quart import Quart, jsonify, request
import os
import aiohttp

app = Quart(__name__)

# ====================================================
# VDS IP ADRESİN
VDS_SOLVER_URL = "http://163.5.53.36:5072/api/solve"
# ====================================================

last_token = None

@app.route('/api/solve', methods=['GET', 'POST'])
async def api_solve():
    args = request.args.to_dict()
    if request.method == 'POST':
        try:
            body = await request.get_json(silent=True)
            if isinstance(body, dict): args.update(body)
        except: pass

    if not args.get('url') or not args.get('sitekey') or not args.get('siteurl'):
        return jsonify({"errorId": 1, "error": "url, sitekey ve siteurl zorunludur"}), 400

    # VDS'de tarayıcının GÖRÜNMESİNİ zorunlu kılıyoruz
    args['visible'] = 'true'

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(VDS_SOLVER_URL, json=args, timeout=15) as resp:
                vds_response = await resp.json()
                return jsonify(vds_response)
    except Exception as e:
        return jsonify({"errorId": 1, "error": f"VDS'e bağlanılamadı: {str(e)}"}), 500

@app.route('/token', methods=['POST'])
async def receive_token():
    global last_token
    try:
        data = await request.json
        token = data.get('token')
        if not token:
            return jsonify({'status': 'error', 'message': 'No token'}), 400
        if token == last_token:
            return jsonify({'status': 'skipped', 'message': 'Duplicate token'})
        
        with open('tokens.txt', 'w') as f:
            f.write(f"{token}\n")
        last_token = token
        return jsonify({'status': 'success', 'token': token[:30] + '...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/tokens', methods=['GET'])
async def get_tokens():
    try:
        with open('tokens.txt', 'r') as f:
            tokens = [t for t in f.read().split('\n') if t.strip()]
        return jsonify({'token': tokens[-1] if tokens else None})
    except FileNotFoundError:
        return jsonify({'token': None, 'message': 'No tokens yet'})

@app.route('/', methods=['GET'])
async def home():
    return jsonify({"service": "Bridge API", "status": "running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
