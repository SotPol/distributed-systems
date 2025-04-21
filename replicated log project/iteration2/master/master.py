from quart import Quart, request, jsonify
import asyncio
from uuid import uuid4
import logging
from aiohttp import ClientSession

app = Quart(__name__)
log = logging.getLogger("MasterNode")
logging.basicConfig(level=logging.INFO, format='[MASTER] %(asctime)s | %(levelname)s | %(message)s')

# Local in-memory storage
logbook = {}
# Define secondary addresses
REPLICAS = ['http://secondary1:5001', 'http://secondary2:5002']

async def forward_to_secondary(target_url, data):
    async with ClientSession() as session:
        try:
            async with session.post(target_url, data=data) as response:
                return response.status == 200
        except Exception as e:
            log.error(f"Failed to reach {target_url}: {e}")
            return False

async def replicate_message(message_id, message, write_quorum):
    confirmations = [True]  # Master counts as 1 ack
    async def push_to_replicas():
        tasks = [forward_to_secondary(f"{url}/replicate", {'msg': message, 'id': message_id}) for url in REPLICAS]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            confirmations.append(result)
            if confirmations.count(True) >= write_quorum:
                break  # Stop early if quorum met

    await push_to_replicas()
    return confirmations

@app.route('/messages', methods=['POST'])
async def handle_post():
    incoming = await request.get_json()
    message = incoming.get('message')
    quorum = int(incoming.get('w', 1))

    if not message:
        return jsonify({"error": "Empty message!"}), 400

    msg_id = str(uuid4())
    logbook[msg_id] = message
    log.info(f"Received message with ID {msg_id}. Quorum required: {quorum}")

    ack_list = await replicate_message(msg_id, message, quorum)

    if ack_list.count(True) >= quorum:
        log.info(f"Quorum {quorum} achieved for {msg_id}.")
        return jsonify({"status": "Replication successful!"}), 200
    else:
        log.error(f"Quorum not reached for {msg_id}. Only {ack_list.count(True)} confirmations.")
        return jsonify({"error": "Replication failed!"}), 500

@app.route('/messages', methods=['GET'])
async def handle_get():
    return jsonify(logbook)

if __name__ == '__main__':
    asyncio.run(app.run_task(host='0.0.0.0', port=25000))
