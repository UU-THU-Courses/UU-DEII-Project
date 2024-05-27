import os
import subprocess
import json
import random

def generate_cluster_summary():
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
        "services": {

        },
        "node_info": []
    }

    # Generate a random identifier
    identifier = random.randint(1000,9999)

    # Generate and fetch results of docker node inspect
    temp_dump_file_1 = f"/temp_{identifier}_node_inspect.json"
    with open(temp_dump_file_1, "w") as outfile:
        subprocess.call(["docker node inspect $(docker node ls -q)"], shell=True, stdout=outfile)
    with open(temp_dump_file_1, "r") as jsonfile:
        json_object = json.load(jsonfile)
    os.remove(temp_dump_file_1)

    for item in json_object:
        response_dict["summary"]["n_nodes"] += 1
        if item["Spec"]["Role"] == "manager": response_dict["summary"]["managers"] += 1
        if item["Spec"]["Role"] == "worker": response_dict["summary"]["workers"] += 1
            
        temp_node = {
            "name": item["Description"]["Hostname"].upper(),
            "role": item["Spec"]["Role"].upper(),
            "addr": item["Status"]["Addr"].upper(),
            "state": item["Status"]["State"].upper(),
            "availability": item["Spec"]["Availability"].upper(),
            "n_containers": 0,
            "containers": [],                
        }

        # Find containers on current node
        temp_dump_file_2 = f"/temp_{identifier}_containers.json"
        with open(temp_dump_file_2, "w") as outfile:
            subprocess.call([f"docker node ps {item['Description']['Hostname']} --format json"], shell=True, stdout=outfile)
        with open(temp_dump_file_2, "r") as jsonfile: 
            containers = [json.loads(obj) for obj in jsonfile.read().splitlines()]
        os.remove(temp_dump_file_2)            
        
        for container in containers:
            temp_node["n_containers"] += 1 if container["DesiredState"] == "Running" else 0
            temp_node["containers"] += [{
                "name": container["Name"],
                "image": container["Image"],
                "status": container["DesiredState"],
                "error": container["Error"],
            }]
        
        response_dict["node_info"] += [temp_node]
    
    # Find service and their statuses
    temp_dump_file_3 = f"/temp_{identifier}_stack_services.json"
    with open(temp_dump_file_3, "w") as outfile:
        subprocess.call([f"docker stack services unittester --format json"], shell=True, stdout=outfile)
    with open(temp_dump_file_3, "r") as jsonfile: 
        services = [json.loads(obj) for obj in jsonfile.read().splitlines()]
    os.remove(temp_dump_file_3)  
    response_dict["services"] = services

    return response_dict