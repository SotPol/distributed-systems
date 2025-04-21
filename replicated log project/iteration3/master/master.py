from quart import Quart, request, jsonify
from uuid import uuid4
from aiohttp import ClientSession
import asyncio
import logging

app = Quart(__name__)
log = logging.getLogger("MasterNode")
logging.basicConfig(level=logging.INFO, format='[MASTER] %(asctime)s | %(levelname)s | %(message)s')

logbook = {}  # {uuid: message}
SECONDARIES = ['http://secondary1:5001', 'http://secondary2:5002']


async def replicate_with_retry(url, data):
    while True:
        try:
            async with ClientSession() as session:
                async with session.post(f"{url}/replicate", json=data) as response:
                    if response.status == 200:
                        return True
        except Exception as e:
            log.error(f"Error replicating to {url}: {e}")
        await asyncio.sleep(2)  # Smart backoff


async def replicate_to_secondaries(message_id, message, w):
    confirmations = [True]  # Master = 1 ack
    data = {"id": message_id, "msg": message}

    tasks = [replicate_with_retry(url, data) for url in SECONDARIES]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        confirmations.append(result)
        if confirmations.count(True) >= w:
            break
    return confirmations


@app.route('/messages', methods=['POST'])
async def submit_message():
    incoming = await request.get_json()
    message = incoming.get('message')
    w = int(incoming.get('w', 1))

    if not message:
        return jsonify({"error": "Invalid message"}), 400

    message_id = str(uuid4())
    logbook[message_id] = message
    log.info(f"Received new message {message_id} with quorum {w}")

    if w == 1:
        # Fire-and-forget replication
        for url in SECONDARIES:
            asyncio.create_task(replicate_with_retry(url, {"id": message_id, "msg": message}))
        return jsonify({"status": "Replication successful!"}), 200
    else:
        confirmations = await replicate_to_secondaries(message_id, message, w)

        if confirmations.count(True) >= w:
            log.info(f"Quorum {w} reached for {message_id}")
            return jsonify({"status": "Replication successful!"}), 200
        else:
            log.error(f"Failed to reach quorum {w} for {message_id}")
            return jsonify({"error": "Replication failed!"}), 500


@app.route('/messages', methods=['GET'])
async def fetch_all_messages():
    return jsonify(logbook)


if __name__ == '__main__':
    asyncio.run(app.run_task(host='0.0.0.0', port=25000))
