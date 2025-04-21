from flask import Flask, request, Response
import httpx
import os
import json
import time
import logging

app = Flask(__name__)
log_storage = []
REPLICA_ADDRESSES = os.getenv('SECONDARY_URLS', '').split(',')

logging.basicConfig(
    level=logging.INFO,
    format='[MASTER] %(asctime)s | %(levelname)s | %(message)s'
)
log = logging.getLogger("MainReplica")

@app.route('/log', methods=['POST'])
def store_message():
    content = request.json
    new_entry = content.get("msg")

    if not new_entry:
        return Response("Invalid message format", status=400)

    log_storage.append(new_entry)
    ack_list = []

    for replica_url in REPLICA_ADDRESSES:
        try:
            r = httpx.post(f"{replica_url}/sync", json={"entry": new_entry}, timeout=10)
            if r.status_code == 200:
                log.info(f"Replication success to {replica_url}")
                ack_list.append(True)
            else:
                log.warning(f"Replica {replica_url} responded with {r.status_code}")
                ack_list.append(False)
        except httpx.RequestError as exc:
            log.error(f"Network issue with {replica_url}: {exc}")
            ack_list.append(False)
            time.sleep(1)

    if all(ack_list):
        return Response(json.dumps({"result": "all replicas acknowledged"}), status=200, mimetype='application/json')
    else:
        return Response(json.dumps({"result": "replication failed"}), status=500, mimetype='application/json')

@app.route('/log', methods=['GET'])
def read_messages():
    log.info("Returning full master log.")
    return Response(json.dumps(log_storage), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=25000)
