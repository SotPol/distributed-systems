from flask import Flask, request, jsonify

app = Flask(__name__)
log_storage = {}

@app.route("/logs", methods=["POST", "GET"])
def handle_logs():
    if request.method == "POST":
        data = request.json
        log_id = data.get("id")
        content = data.get("content")
        
        if not log_id or not content:
            return jsonify({"error": "Missing log ID or content"}), 400
        
        log_storage[log_id] = content
        print(f"[LOGGED] {content}")
        return jsonify({"message": "Log entry saved"}), 201
    
    elif request.method == "GET":
        return jsonify(log_storage), 200

if __name__ == "__main__":
    app.run(port=5001)