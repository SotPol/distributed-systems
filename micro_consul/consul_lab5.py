from random import choice
import consul
import json
import uuid

client = consul.Consul(host="127.0.0.1", port=8500)

def register_service(name, port):
    service_id = str(uuid.uuid4())
    client.agent.service.register(
        name, service_id, address="localhost", port=port
    )
    return service_id

def deregister_service(service_id):
    client.agent.service.deregister(service_id)

def get_service_address_port(name):
    services = [
        f"http://{info['Address']}:{info['Port']}"
        for info in client.agent.services().values()
        if info['Service'] == name
    ]
    return choice(services) if services else None

def store_key_value(key, value):
    client.kv.put(key, value)

def get_key_value(key):
    index, data = client.kv.get(key)
    return data['Value'] if data else None

hz_settings = {
    "cluster_name": "dev",
    "cluster_members": ["127.0.0.1:5701", "127.0.0.1:5702", "127.0.0.1:5703"],
    "map_name": "messages",
}
mq_settings = {"queue_name": "message-queue"}

store_key_value('hz_configs', json.dumps(hz_settings))
store_key_value('mq_configs', json.dumps(mq_settings))