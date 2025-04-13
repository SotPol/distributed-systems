from flask import Flask, request, jsonify
import hazelcast
import argparse
import consul_lab5
import subprocess
import json

parser = argparse.ArgumentParser(description="Start Logging Service")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

subprocess.Popen(["./hz", "start"])

service_id = consul_lab5.register_service("logging-service", args.port)

config_data = consul_lab5.get_key_value("hz_configs")
if not config_data:
    print("No Hazelcast configuration found.")
    exit(1)

hz_config = json.loads(config_data)
hazelcast_client = hazelcast.HazelcastClient(
    cluster_name=hz_config["cluster_name"],
    cluster_members=hz_config["cluster_members"]
)
log_store = hazelcast_client.get_map(hz_config["map_name"]).blocking()

app = Flask(__name__)

@app.route('/logs', methods=['POST'])
def store_log():
    data = request.get_json()
    log_store.put(data['id'], data['message'])
    print(f"[LOGGED] {data['message']}")
    return jsonify({"status": "success"}), 200

@app.route('/logs', methods=['GET'])
def retrieve_logs():
    all_logs = {key: log_store.get(key) for key in log_store.key_set()}
    return jsonify(all_logs), 200

if __name__ == '__main__':
    app.run(port=args.port)
    input("Press Enter to stop service...\n")
    consul_lab5.deregister_service(service_id)