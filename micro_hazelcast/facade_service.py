from flask import Flask, request, jsonify
import uuid
import requests
import random

app = Flask(__name__)

CONFIG_SERVER_URL = "http://localhost:6000/services"

def get_instances(service_name):
    try:
        response = requests.get(f"{CONFIG_SERVER_URL}/{service_name}")
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"[ERROR] Failed to get service instances: {e}")
    return []

@app.route("/", methods=["POST"])
def route_message():
    incoming = request.get_json()
    user_msg = incoming.get("msg")
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    generated_id = str(uuid.uuid4())
    logging_instances = get_instances("logging-service")
    if not logging_instances:
        return jsonify({"error": "No logging-service available"}), 503

    instance = random.choice(logging_instances)
    log_url = f"http://{instance['host']}:{instance['port']}/logs"

    try:
        log_response = requests.post(log_url, json={"id": generated_id, "message": user_msg})
    except Exception as e:
        return jsonify({"error": "Logging failed", "detail": str(e)}), 500

    if not log_response.ok:
        return jsonify({"error": "Log server error"}), 400

    return jsonify({
        "logging_feedback": log_response.json(),
        "facade_info": {"id": generated_id, "message": user_msg}
    }), 200

@app.route("/", methods=["GET"])
def aggregate_data():
    logging_instances = get_instances("logging-service")
    msg_instances = get_instances("messages-service")

    if not logging_instances or not msg_instances:
        return jsonify({"error": "One or more services unavailable"}), 503

    instance_log = random.choice(logging_instances)
    instance_msg = random.choice(msg_instances)

    try:
        log_data = requests.get(f"http://{instance_log['host']}:{instance_log['port']}/logs").json()
        msg_data = requests.get(f"http://{instance_msg['host']}:{instance_msg['port']}/messages").json()
    except Exception as e:
        return jsonify({"error": "Service request failed", "detail": str(e)}), 500

    return jsonify({
        "logs": log_data,
        "messages": msg_data
    }), 200

if __name__ == "__main__":
    app.run(port=5000)