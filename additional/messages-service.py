from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/messages", methods=["GET"])
def fetch_messages():
    return jsonify({"message": "Feature not implemented yet"}), 200

if __name__ == "__main__":
    app.run(port=5002)