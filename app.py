from flask import Flask, jsonify, request
from flask_cors import CORS
from log_server import LogServer

app = Flask(__name__)
CORS(app)

log_server = LogServer()

@app.route("/api/v1/health")
def health():
    return log_server.health_check()

@app.route("/api/v1/logs", methods=["GET"])
def get_logs():
    return log_server.get_logs()

@app.route("/api/v1/logs", methods=["POST"])
def create_log():
    data = request.get_json()
    return log_server.create_log(data)

@app.route("/api/v1/logs", methods=["DELETE"])
def clear_logs():
    return log_server.clear_logs()

@app.route("/api/v1/logs/populate", methods=["POST"])
def populate_logs():
    return log_server.random_log()

@app.route("/api/v1/logs/<int:log_id>", methods=["DELETE"])
def delete_log(log_id):
    return log_server.delete_log(log_id)

@app.route("/api/v1/services", methods=["GET"])
def get_services():
    return log_server.get_services()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
