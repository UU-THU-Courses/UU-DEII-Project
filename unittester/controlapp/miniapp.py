import requests, subprocess
import argparse
from flask import (
   Flask,
   request,
   session
)

app = Flask(__name__)

@app.route("/send-token", methods=["POST"])
def send_token():
    global manager
    if manager:
        if request.method == "POST":
            with open("/swarm-token.txt", "r") as f:
                token = f.readline().strip()
                r = requests.post(f"http://{request.form['worker_ip']}:5200/init-node", data={"manager-addr": request.form["head_ip"], "manager-port": 2377, "swarm-token": f"{token}"})
            return "Success", 200
        else:
            return "Failure", 400
    else:
        return "Not a manager", 400

@app.route("/init-node", methods=["POST"])
def init_node():
    global manager
    if not manager:
        if request.method == "POST":
            manager_addr = request.form["manager-addr"]
            manager_port = request.form["manager-port"]
            swarm_token = request.form["swarm-token"].strip()
            run_command = rf"docker swarm join --token {swarm_token} {manager_addr}:{manager_port}"
            subprocess.call(run_command, shell=True)
            return "Success", 200
        else:
            return "Failure", 400
    else:
        return "Not a worker node", 400
    
@app.route("/drain-node", methods=["POST"])
def drain_node():
    global manager
    if not manager:
        if request.method == "POST":
            #print(request.args)
            return "Success", 200
        else:
            return "Failure", 400
    else:
        return "Not a worker node", 400

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
    parser.add_argument(
        "--manager",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    global manager
    manager = args.manager

    app.run(host = args.host,port=args.port,debug=args.debug)
