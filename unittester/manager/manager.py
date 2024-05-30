import os
import random
import argparse
import subprocess

import json
from helpers import generate_cluster_summary
from flask import (
   Flask,
   request,
   Response
)

app = Flask(__name__)

@app.route("/send-token", methods=["GET"])
def send_token():
    if request.method == "GET":
        # Read the latest swarm token
        with open("/swarm-worker-token.txt", "r") as f:
            token = f.readline().strip()
        # request.args contains any desired 
        # parameters sent from the worker node
        data_dict = { "swarm-token": token, "manager-port": 2377 }
        return Response(json.dumps(data_dict), 200)
    else:
        return Response("Only GET available!", 400)

@app.route("/run-workers", methods=["POST"])
def fill_node():    
    if request.method == "POST":
        subprocess.call(f"bash /project/unittester/manager/scripts/scaleup.sh {request.args['count']}", shell=True)
        return Response("Success!", 200)
    else:
        return Response("Only POST available!", 400)

@app.route("/drain-node", methods=["POST"])
def drain_node():
    if request.method == "POST":
        log_fpath = f"/drain_log_{random.randint(1000, 9999)}.txt"
        node_count = request.args["node_count"]
        subprocess.call(f"bash /project/unittester/manager/scripts/drain.sh {node_count} {log_fpath}", shell=True)
        node_names = []
        if os.path.exists(log_fpath):
            with open(log_fpath) as logfile:
                node_names = logfile.read().splitlines()
            os.remove(log_fpath)
        return Response(json.dumps({"nodes": node_names}), 200)
    else:
        return Response("Only POST available!", 400)

@app.route("/summary", methods=["GET"])
def cluster_summary():
    if request.method == "GET":
        response_dict = generate_cluster_summary()
        return Response(json.dumps(response_dict), 200)
    else:
        return Response("Only GET available!", 400)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        required=False,
        default="0.0.0.0",
        type=str,
    )
    parser.add_argument(
        "--port",
        required=False,
        default=5200,
        type=int,
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    app.run(host = args.host,port=args.port,debug=args.debug)
