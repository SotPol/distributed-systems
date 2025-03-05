from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

LOG_SERVICE_URL = "http://localhost:5001/logs"
MSG_SERVICE_URL = "http://localhost:5002/messages"

def send_to_logging_service(msg_id, content):
    payload = {"id": msg_id, "content": content}
    response = requests.post(LOG_SERVICE_URL, json=payload)
    return response

def fetch_service_data():
    logs = requests.get(LOG_SERVICE_URL).json()
    messages = requests.get(MSG_SERVICE_URL).json()
    return logs, messages

@app.route("/", methods=["POST", "GET"])
def process_request():
    if request.method == "POST":
        content = request.json.get("message")
        if not content:
            return jsonify({"error": "No message received"}), 400
        
        message_id = str(uuid.uuid4())
        log_response = send_to_logging_service(message_id, content)
        
        if log_response.status_code not in range(200, 300):
            return jsonify({"error": "Failed to log message"}), 500
        
        return jsonify({
            "status": "Message logged",
            "message_id": message_id,
            "content": content
        }), 201
    
    elif request.method == "GET":
        logs, messages = fetch_service_data()
        return jsonify({"logs": logs, "messages": messages}), 200

if __name__ == "__main__":
    app.run(port=5000)