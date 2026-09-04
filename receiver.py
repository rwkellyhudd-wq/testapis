from quart import Quart, jsonify, request
import os

app = Quart(__name__)

@app.route('/token', methods=['POST'])
async def receive_token():
    try:
        data = await request.json
        token = data.get('token')
        
        if not token:
            return jsonify({'status': 'error', 'message': 'No token provided'}), 400
        
        # ESKİ TOKEN'I SİL, YENİSİNİ YAZ!
        with open('tokens.txt', 'w') as f:  # 'w' = üzerine yaz
            f.write(f"{token}\n")
        
        return jsonify({'status': 'success', 'token': token[:30] + '...'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/tokens', methods=['GET'])
async def get_tokens():
    try:
        with open('tokens.txt', 'r') as f:
            tokens = f.read().split('\n')
        tokens = [t for t in tokens if t.strip()]
        
        if tokens:
            # SADECE SON TOKEN'I GÖSTER
            return jsonify({'token': tokens[-1]})
        else:
            return jsonify({'token': None, 'message': 'No tokens yet'})
    except FileNotFoundError:
        return jsonify({'token': None, 'message': 'No tokens yet'})
    except:
        return jsonify({'token': None, 'message': 'Error reading tokens'})

@app.route('/', methods=['GET'])
async def home():
    try:
        with open('tokens.txt', 'r') as f:
            tokens = f.read().split('\n')
            tokens = [t for t in tokens if t.strip()]
        
        return jsonify({
            'service': 'Token Receiver',
            'status': 'running',
            'last_token': tokens[-1] if tokens else None,
            'total_tokens_stored': len(tokens)  # Her zaman 1 olacak
        })
    except FileNotFoundError:
        return jsonify({
            'service': 'Token Receiver',
            'status': 'running',
            'last_token': None,
            'total_tokens_stored': 0
        })
    except:
        return jsonify({
            'service': 'Token Receiver',
            'status': 'error',
            'last_token': None
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
