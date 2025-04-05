from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/messages", methods=["GET"])
def get_static_message():
    response = {"message": "functionality pending"}
    return jsonify(response), 200

if __name__ == "__main__":
    app.run(port=5005)