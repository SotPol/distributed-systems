from flask import Flask, jsonify

app = Flask(__name__)

# Простий реєстр мікросервісів
services_registry = {
    "logging-service": [
        "http://localhost:5001",
        "http://localhost:5002",
        "http://localhost:5003"
    ],
    "messages-service": [
        "http://localhost:5004"
    ]
}

@app.route("/service/<service_name>", methods=["GET"])
def get_service_instances(service_name):
    instances = services_registry.get(service_name)
    if instances is None:
        return jsonify({"error": "Service not found"}), 404
    return jsonify({"instances": instances})

if __name__ == "__main__":
    app.run(port=5010)

