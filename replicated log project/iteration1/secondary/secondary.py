from flask import Flask, request, Response
import os
import time
import json
import logging

app = Flask(__name__)
replica_data = []

logging.basicConfig(
    level=logging.INFO,
    format='[SECONDARY] %(asctime)s | %(levelname)s | %(message)s'
)
log = logging.getLogger("ReplicaNode")

REPLICA_PORT = os.getenv('PORT', '5001')

@app.route('/sync', methods=['POST'])
def sync_message():
    content = request.json
    message = content.get('entry')

    if not message:
        return Response("Empty message", status=400)

    time.sleep(5)  # artificial network delay simulation
    replica_data.append(message)
    log.info(f"Message synchronized: {message}")
    return Response(json.dumps({"ack": True}), status=200, mimetype='application/json')

@app.route('/log', methods=['GET'])
def fetch_replica_log():
    log.info("Providing replica log snapshot.")
    return Response(json.dumps(replica_data), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(REPLICA_PORT))
