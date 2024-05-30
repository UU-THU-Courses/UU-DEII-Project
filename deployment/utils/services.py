import time
import requests
import subprocess
import fire

def query_swarm_token(manager_addr, worker_addr):
    # Wait until the swarm token file 
    # is not available at head node
    status_code = -1
    print(f"\nWorker {worker_addr}: Querying manager at {manager_addr} for swarm token ...")
    while status_code != 200:
        try:
            response = requests.get(f"http://{manager_addr}:5200/send-token", params={"worker_ip": worker_addr}, timeout=5)
            status_code = response.status_code
            print(f"Got status code: {status_code} ...")
        except:
            print("Exception was thrown ...")
            status_code = -1
        
        if status_code != 200:
            print("GET link not available sleeping for 120 seconds ...")
            time.sleep(120)

    # Convert response to json                
    response_dict = response.json()

    # Return the requested fields
    return response_dict["swarm-token"].strip(), response_dict["manager-port"]

def join_swarm(worker_addr):

    # Attempt to read the manager address
    # from HEAD-IP.txt file at root path
    while True:
        try:
            with open("/HEAD-IP.txt", "r") as f:
                manager_addr = f.read().strip()
            break
        except:
            print("Waiting 120 seconds before attempting to read HEAD-IP.txt again ...")
            time.sleep(120)

    # Query the controller application of 
    # manager node and get swarm token
    swarm_token, manager_port = query_swarm_token(manager_addr, worker_addr)

    # Make subprocess call to join the swarm
    run_command = rf"docker swarm join --token {swarm_token} {manager_addr}:{manager_port}"
    subprocess.call(run_command, shell=True)

def request_workload():
    # Attempt to read the manager address
    # from HEAD-IP.txt file at root path
    while True:
        try:
            with open("/HEAD-IP.txt", "r") as f:
                manager_addr = f.read().strip()
            break
        except:
            print("Waiting 120 seconds before attempting to read HEAD-IP.txt again ...")
            time.sleep(120)

    # Wait until the swarm token file 
    # is not available at head node
    status_code = -1
    while status_code != 200:
        try:
            response = requests.post(f"http://{manager_addr}:5200/run-workers", params={"count": 32}, timeout=5)
            status_code = response.status_code
            print(f"Got status code: {status_code} ...")
        except:
            print("Exception was thrown ...")
            status_code = -1
        
        if status_code != 200:
            print("POST link not available sleeping for 120 seconds ...")
            time.sleep(120)


if __name__ == "__main__":
    fire.Fire({
        "--join-swarm": join_swarm,
        "--add-workload": request_workload,
    })