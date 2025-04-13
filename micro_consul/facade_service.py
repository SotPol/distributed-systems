from flask import Flask, request, jsonify
import requests
import hazelcast
import argparse
import consul_lab5
import uuid
import json

parser = argparse.ArgumentParser(description="Start Facade Service")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

facade_id = consul_lab5.register_service("facade-service", args.port)

hz_config_data = consul_lab5.get_key_value("hz_configs")
if hz_config_data:
        hz_config = json.loads(hz_config_data)
        print("Hazelcast configuration: ", hz_config)
else:
    print("Missing Hazelcast configuration in Consul.")
    exit(1)

hz_settings = json.loads(hz_config_data)

mq_config_data = consul_lab5.get_key_value("mq_configs")
if mq_config_data:
        mq_config = json.loads(mq_config_data)
        print("Message Queue configuration: ", mq_config)
else:
    print("Missing Message Queue configuration in Consul.")
    exit(1)

mq_settings = json.loads(mq_config_data)

hazelcast_client = hazelcast.HazelcastClient(
    cluster_name=hz_settings["cluster_name"],
    cluster_members=hz_settings["cluster_members"]
)
message_queue = hazelcast_client.get_queue(mq_settings["queue_name"]).blocking()

app = Flask(__name__)

@app.route('/', methods=['POST'])
def submit_message():
    logging_service_url = consul_lab5.get_service_address_port("logging-service")
    msg = request.json.get("msg")
    msg_id = str(uuid.uuid4())

    if not msg:
        return "No message provided", 400

    response = requests.post(
        f"{logging_service_url}/logs",
        json={"id": msg_id, "message": msg}
    )

    if response.status_code not in range(200, 300):
        return "Failed to log the message", 400

    message_queue.offer(msg)

    return jsonify({
        "logging_service": json.loads(response.text),
        "facade_service": {"id": msg_id, "message": msg}
    }), 200

@app.route('/', methods=['GET'])
def fetch_logs_and_messages():
    logging_url = f"{my_consul.get_service_address_port('logging-service')}/logs"
    messages_url = f"{my_consul.get_service_address_port('messages-service')}/messages"

    logs = requests.get(logging_url).json()
    messages = requests.get(messages_url).json()

    return jsonify({"logs": logs, "messages": messages}), 200

if __name__ == '__main__':
    app.run(port=args.port)
    input("Press Enter to shut down...\n")
    consul_lab5.deregister_service(facade_id)