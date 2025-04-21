from flask import Flask, request, jsonify
import time, threading

app = Flask(__name__)
storage = {}
lock = threading.Lock()

@app.route('/replicate', methods=['POST'])
def replicate():
    incoming = request.get_json()
    msg_id = incoming.get("id")
    msg = incoming.get("msg")

    if msg_id and msg:
        time.sleep(5)  # simulate network delay
        with lock:
            if msg_id not in storage:
                storage[msg_id] = msg
                return jsonify({"ack": True}), 200
            else:
                return jsonify({"info": "Duplicate ignored"}), 200
    return jsonify({"error": "Invalid data"}), 400


@app.route('/messages', methods=['GET'])
def get_messages():
    ordered = dict(sorted(storage.items()))
    return jsonify(ordered)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # secondary2
