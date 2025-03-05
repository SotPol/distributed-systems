from flask import Flask, request, jsonify
import requests
import uuid
import time

app = Flask(__name__)

LOGGING_SERVICE_URL = "http://localhost:5001/log"

def send_with_retry(msg_id, content, retries=3, delay=2):
    """Відправка POST-запиту з повторенням у разі невдачі та логуванням у консоль"""
    for attempt in range(retries):
        try:
            print(f"[{attempt + 1}/{retries}] Sending log {msg_id} to {LOGGING_SERVICE_URL}...")
            response = requests.post(LOGGING_SERVICE_URL, json={"id": msg_id, "content": content}, timeout=5)
            
            if response.status_code in [200, 201]:  # 200 (OK), 201 (Created)
                print(f"[SUCCESS] Log {msg_id} saved successfully.")
                return response.json()
            else:
                print(f"[ERROR] Log {msg_id} failed with status {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[{attempt + 1}/{retries}] Failed to send log {msg_id}: {e}")

        time.sleep(delay)  # Затримка перед наступною спробою
    
    print(f"[FAILED] Log {msg_id} could not be saved after {retries} retries.")
    return {"error": "Failed to log message after retries"}

@app.route("/", methods=["POST", "GET"])
def process_request():
    if request.method == "POST":
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "No message received"}), 400
        
        message_id = str(uuid.uuid4())
        log_status = send_with_retry(message_id, data["message"])

        return jsonify({
            "status": log_status,
            "message_id": message_id,
            "content": data["message"]
        }), 201

    elif request.method == "GET":
        try:
            response = requests.get("http://localhost:5001/logs", timeout=5)
            return jsonify(response.json()), response.status_code
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Failed to fetch logs - {e}"}), 500

if __name__ == "__main__":
    app.run(port=5000)
