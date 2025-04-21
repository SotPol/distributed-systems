from flask import Flask, request, jsonify
import time, random

app = Flask(__name__)
mirror_storage = {}

def random_network_lag():
    time.sleep(random.randint(4, 12))

@app.route('/replicate', methods=['POST'])
def save_replica():
    msg = request.form.get('msg')
    msg_id = request.form.get('id')

    if not msg or not msg_id:
        return jsonify({"error": "Invalid input"}), 400

    if msg_id not in mirror_storage:
        random_network_lag()  # simulate delivery lag
        mirror_storage[msg_id] = msg
        return jsonify({"ack": True}), 200
    return jsonify({"info": "Duplicate ignored"}), 200

@app.route('/messages', methods=['GET'])
def list_replicated():
    return jsonify(mirror_storage)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
