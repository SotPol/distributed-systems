from flask import Flask, request, jsonify
import hazelcast
import requests
import uuid
import json
from pyotp import random

app = Flask(__name__)

# Initialize Hazelcast client and connect to message queue
hz_client = hazelcast.HazelcastClient(cluster_name="dev", cluster_members=[])
queue = hz_client.get_queue("message-queue").blocking()

@app.route('/', methods=['POST'])
def post_message():
    data = request.get_json()
    message = data.get("msg")
    message_id = str(uuid.uuid4())

    if not message:
        return "No message provided", 400

    # Randomly select a logging service port
    target_port = random.randint(5001, 5003)
    log_endpoint = f"http://localhost:{target_port}/logs"

    # Send message to logging service
    log_response = requests.post(log_endpoint, json={'id': message_id, 'message': message})

    if not log_response.ok:
        return "Logging service error", 400

    # Send message to the Hazelcast queue
    queue.offer(message)

    return jsonify({
        "logging_response": json.loads(log_response.text),
        "facade_info": {"id": message_id, "message": message}
    }), 200

@app.route('/', methods=['GET'])
def fetch_logs_and_messages():
    log_port = random.randint(5001, 5003)
    msg_port = random.randint(5004, 5005)

    logs = requests.get(f"http://localhost:{log_port}/logs").json()
    messages = requests.get(f"http://localhost:{msg_port}/messages").json()

    return jsonify({"logs": logs, "messages": messages}), 200

if __name__ == "__main__":
    app.run(port=5000)