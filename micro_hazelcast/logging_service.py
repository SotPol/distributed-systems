from flask import Flask, request, jsonify
import hazelcast
import subprocess
import argparse

# Ініціалізація аргументів командного рядка
cli_parser = argparse.ArgumentParser()
cli_parser.add_argument("--port", type=int, required=True)
port_arg = cli_parser.parse_args().port

# Запуск Hazelcast сервера як окремого процесу
subprocess.Popen(["hz", "start"])

# Підключення до клієнта Hazelcast
hz_client = hazelcast.HazelcastClient(cluster_name="dev", cluster_members=[])
log_map = hz_client.get_map("messages").blocking()

# Ініціалізація Flask
app = Flask(__name__)

@app.route("/logs", methods=["POST"])
def add_log_entry():
    payload = request.get_json()
    entry_id = payload["id"]
    entry_message = payload["message"]
    
    log_map.put(entry_id, entry_message)
    print(f"[INFO] Log added: {entry_message}")
    
    return jsonify({"result": "stored"}), 200

@app.route("/logs", methods=["GET"])
def fetch_all_logs():
    logs = {key: log_map.get(key) for key in log_map.key_set()}
    return jsonify(logs), 200

if __name__ == "__main__":
    app.run(port=port_arg)