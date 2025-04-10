from flask import Flask, request, jsonify
import hazelcast
import argparse
import subprocess

# Launch Hazelcast instance
subprocess.Popen(["hz", "start"])

# Parse command-line port argument
parser = argparse.ArgumentParser(description="Logging Service")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

# Hazelcast connection and map
hz_client = hazelcast.HazelcastClient(cluster_name="dev", cluster_members=[])
log_store = hz_client.get_map("messages").blocking()

app = Flask(__name__)

@app.route('/logs', methods=['POST'])
def store_log():
    payload = request.json
    log_store.put(payload['id'], payload['message'])
    print(f"[Stored] {payload['message']}")
    return jsonify({"status": "logged"}), 200

@app.route('/logs', methods=['GET'])
def retrieve_logs():
    entries = {key: log_store.get(key) for key in log_store.key_set()}
    return jsonify(entries), 200

if __name__ == '__main__':
    app.run(port=args.port)