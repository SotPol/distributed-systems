from flask import Flask, jsonify
import hazelcast
import argparse
from threading import Thread

# Parse incoming port argument
parser = argparse.ArgumentParser(description="Message Service")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

# Setup Hazelcast and message queue
hz_client = hazelcast.HazelcastClient(cluster_name="dev", cluster_members=[])
msg_queue = hz_client.get_queue("message-queue").blocking()
received_msgs = []

# Background thread to consume from queue
def listen_for_messages():
    while True:
        msg = msg_queue.take()
        received_msgs.append(msg)
        print(f"New message: {msg}")

thread = Thread(target=listen_for_messages, daemon=True)
thread.start()

app = Flask(__name__)

@app.route('/messages', methods=['GET'])
def get_messages():
    if received_msgs:
        return jsonify({f"messages from port {args.port}": received_msgs}), 200
    return "No messages available", 200

if __name__ == '__main__':
    app.run(port=args.port)