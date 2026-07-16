from flask import Flask, jsonify, request
from flask_cors import CORS
from config import MONGO_URI, DB_NAME
from log_server import LogServer

import pymongo
import random

app = Flask(__name__)
CORS(app)

def randomMessage():
    arr = ["wolf", "dog", "cat", "sheep", "bull", "fish", "lizard", "frog", "toad", "sheep", "lion"]
    msg = ""

    for i in range(random.randint(1, 20)):
        msg = msg + " " + random.choice(arr)

    return msg

@app.route("/")
def index():
    return jsonify({"message": "Hello, World!"})


@app.route("/logs/clearLogs", methods=["DELETE"])
def clearLogs():
    result = db.logs.delete_many({})
    return jsonify({"deleted": result.deleted_count}), 200

@app.route("/logs/update", methods=["POST"])
def updateLog():

    #Update the current log_server and create update the logger service 
    data = request.get_json()
    return jsonify(data)

@app.route("/logs/populate")
def populateLog():
    from datetime import datetime

    levelArr = ["INFO", "ERROR", "WARN"]
    serviceArr = ["auth", "api-gateway", "user-service", "payments", "scheduler", "email-service", "search"]

    for i in range(10):
        hashMap = {
            "level": random.choice(levelArr),
            "message": randomMessage(),
            "service": random.choice(serviceArr),
            "timestamp": datetime.utcnow().isoformat()
        }

        log_server.logAppend(hashMap)
        db.logs.insert_one(hashMap)

    return jsonify({"status": "ok"}), 201


@app.route("/logs", methods=["POST"])
def appendLog():
    data = request.get_json()
    if isinstance(data, list):
        for log in data:
            log_server.logAppend(log)
        db.logs.insert_many(data)
    else:
        log_server.logAppend(data)
        db.logs.insert_one(data)

    return jsonify({"status": "ok"}), 201

@app.route("/database", methods=["GET"])
def getDatabase():
    logs = list(db.logs.find())
    for log in logs:
        log["_id"] = str(log["_id"])
    return jsonify(logs)

@app.route("/logs/<log_id>", methods=["DELETE"])
def deleteLog(log_id):
    from bson import ObjectId
    db.logs.delete_one({"_id": ObjectId(log_id)})
    return jsonify({"status": "ok"})

@app.route("/logs/recent", methods=["GET"])
def getLogs():
    res = log_server.getRecentLogs()
    return f"{res}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
