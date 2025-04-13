from flask import Flask, jsonify
from threading import Thread
import hazelcast
import argparse
import consul_lab5
import json

parser = argparse.ArgumentParser(description="Launch Messages Service")
parser.add_argument("--port", type=int, required=True)
args = parser.parse_args()

service_id = consul_lab5.register_service("messages-service", args.port)
stored_messages = []

hz_config_data = consul_lab5.get_key_value("hz_configs")
if hz_config_data:
        hz_config = json.loads(hz_config_data)
        print("Hazelcast configuration: ", hz_config)
else:
    print("Missing Hazelcast configuration in Consul.")
    exit(1)

mq_config_data = consul_lab5.get_key_value("mq_configs")
if mq_config_data:
        mq_config = json.loads(mq_config_data)
        print("Message Queue configuration: ", mq_config)
else:
    print("Missing Message Queue configuration in Consul.")
    exit(1)

hz_settings = json.loads(hz_config_data)
mq_settings = json.loads(mq_config_data)

hazelcast_client = hazelcast.HazelcastClient(
    cluster_name=hz_settings["cluster_name"],
    cluster_members=hz_settings["cluster_members"]
)
message_queue = hazelcast_client.get_queue(mq_settings["queue_name"]).blocking()

def queue_listener():
    while True:
        msg = message_queue.take()
        stored_messages.append(msg)
        print(f"Consumed message: {msg}")

listener_thread = Thread(target=queue_listener, daemon=True)
listener_thread.start()

app = Flask(__name__)

@app.route('/messages', methods=['GET'])
def list_messages():
    return (
        jsonify({f"Service on port {args.port}": stored_messages}) 
        if stored_messages 
        else ("No messages available.", 200)
    )

if __name__ == '__main__':
    app.run(port=args.port)
    input("Press Enter to stop service...\n")
    consul_lab5.deregister_service(service_id)