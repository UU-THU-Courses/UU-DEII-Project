import os
import random
import argparse
import subprocess

import json
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
        subprocess.call("bash /project/unittester/manager/scripts/scaleup.sh", shell=True)
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
        # Read the latest swarm token
        with open("/swarm-worker-token.txt", "r") as f:
            worker_token = f.readline().strip()
        with open("/swarm-manager-token.txt", "r") as f:
            manager_token = f.readline().strip()

        # Build response dictionary
        response_dict = { 
            "summary": {
                "n_nodes": 0,
                "managers": 0,
                "workers": 0,
                "manager_token": manager_token,
                "worker_token": worker_token,                
            }, 
            "node_info": []
        }

        # Generate a random identifier
        identifier = random.randint(1000,9999)

        # Generate and fetch results of docker node inspect
        temp_dump_file = f"/temp_{identifier}_node_inspect.json"
        with open(temp_dump_file, "w") as outfile:
            subprocess.call(["docker node inspect $(docker node ls -q)"], shell=True, stdout=outfile)
        with open(temp_dump_file, "r") as jsonfile:
            json_object = json.load(jsonfile)
        os.remove(temp_dump_file)

        for item in json_object:
            response_dict["summary"]["n_nodes"] += 1
            if item["Spec"]["Role"] == "manager": response_dict["summary"]["managers"] += 1
            if item["Spec"]["Role"] == "worker": response_dict["summary"]["workers"] += 1
                
            temp_node = {
                "name": item["Description"]["Hostname"].upper(),
                "role": item["Spec"]["Role"].upper(),
                "addr": item["Status"]["Addr"].upper(),
                "status": item["Status"]["State"].upper(),
                "n_containers": 0,
                "containers": [],                
            }

            # Find containers on current node
            temp_dump_file_2 = f"/temp_{identifier}_node_inspect.json"
            with open(temp_dump_file_2, "w") as outfile:
                subprocess.call([f"docker node ps {item['Description']['Hostname']} --format json"], shell=True, stdout=outfile)
            with open(temp_dump_file_2, "r") as jsonfile: 
                containers = [json.loads(obj) for obj in jsonfile.read().splitlines()]
            os.remove(temp_dump_file_2)            
            
            for container in containers:
                temp_node["n_containers"] += 1
                temp_node["containers"] += [{
                    "name": container["Name"],
                    "image": container["Image"],
                    "status": container["DesiredState"],
                    "error": container["Error"],
                }]
            
            response_dict["node_info"] += [temp_node]

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
