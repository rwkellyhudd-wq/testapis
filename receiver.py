from quart import Quart, jsonify, request
import os
import aiohttp
import uuid
import asyncio

app = Quart(__name__)

VDS_SOLVER_URL = "http://163.5.53.36:5072/api/solve"

# Task ID'ye göre token'ları tutacağımız hafıza
TOKEN_QUEUE = {}

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

    # Her istek için benzersiz bir Task ID üret
    task_id = str(uuid.uuid4())
    args['task_id'] = task_id
    args['visible'] = 'true' # VDS'de tarayıcı görünsün (test için)

    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.post(VDS_SOLVER_URL, json=args, timeout=15) as resp:
                vds_response = await resp.json()
                # VDS'den gelen cevabı aynen dön (içinde task_id var)
                return jsonify(vds_response)
    except Exception as e:
        return jsonify({"errorId": 1, "error": f"VDS'e bağlanılamadı: {str(e)}"}), 500

@app.route('/token', methods=['POST'])
async def receive_token():
    try:
        data = await request.json
        token = data.get('token')
        task_id = data.get('task_id')

        if not token or not task_id:
            return jsonify({'status': 'error', 'message': 'Token veya Task ID eksik'}), 400
        
        # Token'ı ilgili Task ID'nin kutusuna koy
        TOKEN_QUEUE[task_id] = token
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/get_token', methods=['GET'])
async def get_token():
    # Kullanıcıdan task_id parametresi bekliyoruz
    task_id = request.args.get('task_id')
    if not task_id:
        return jsonify({"error": "task_id parametresi gerekli"}), 400

    # Eğer o Task ID'ye ait bir token geldiyse ver
    if task_id in TOKEN_QUEUE:
        token = TOKEN_QUEUE[task_id]
        del TOKEN_QUEUE[task_id] # Token'ı verdik, hafızadan sil
        return jsonify({"status": "success", "token": token})
    else:
        return jsonify({"status": "pending", "message": "Token henüz hazır değil"}), 202

@app.route('/', methods=['GET'])
async def home():
    return jsonify({"service": "Bridge API", "status": "running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
