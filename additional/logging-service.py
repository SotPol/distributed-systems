from flask import Flask, request, jsonify

app = Flask(__name__)
log_storage = {}  # {log_id: content}

@app.route("/log", methods=["POST"])
def log_message():
    data = request.get_json()
    log_id = data.get("id")
    content = data.get("content")

    if not log_id or not content:
        return jsonify({"error": "Invalid log entry"}), 400

    if log_id in log_storage:  # Перевіряємо, чи такий log_id вже існує
        return jsonify({"message": "Duplicate log entry ignored"}), 409

    log_storage[log_id] = content
    print(f"[LOGGED] {content}")
    return jsonify({"message": "Log entry saved"}), 201

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(log_storage), 200

if __name__ == "__main__":
    app.run(port=5001)
