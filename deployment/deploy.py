import os
import fire
import random
import requests, time

from utils.requisition import create_instance
from utils.configs import parse_configs, write_configs

MAX_ATTEMPTS = 10

def deploy_headnode(name_prefix, configs):
    """A module to create the headnode and send config files."""
    
    # Create the headnode and obtain ip address
    ip_addr = create_instance(name=f"{name_prefix}-headnode", configs=configs)

    return ip_addr

def launch_workernodes(name_prefix, num_nodes, head_ip, configs):
    # Update cloud configurations in order to write
    # the head ip address to a temporary file at
    # worker node
    
    cloud_cfg = parse_configs(config_path=configs["instance_configs"])
    configs["instance_configs"] = "__temp_dir__/temp_cloud_cfg.yaml"

    cloud_cfg["write_files"] = [{
        "encoding": "b64",
        "content": head_ip,
        "owner": "root:root",
        "path": "/HEAD-IP.txt",
        "permissions": "0644",
    }]
    os.makedirs("__temp_dir__", exist_ok=True)
    write_configs(configs["instance_configs"], cloud_cfg)

    # Deploy all nodes
    ip_addresses = []
    for i in range(num_nodes):
        # Create the headnode and obtain ip address
        ip_addresses += [create_instance(name=f"{name_prefix}-worker-{i+1}", configs=configs)]
        print(f"Worker-{i+1} deployed at {ip_addresses[-1]} ...")

    # Retrun worker ip addresses
    return ip_addresses

def del_workernode(node_ip):
    pass

def add_workernode(num_nodes, head_ip, config_file="configs/deploy-cfg.yaml"):
    # Open the configurations file
    print("Parsing provided configurations file... ")
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Obtain the swarm token
    # docker swarm join-token manager -q
    worker_ips = launch_workernodes(name_prefix=f"UZ-{identifier}", num_nodes=num_nodes, head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"])

def full_deployment(config_file = "configs/deploy-cfg.yaml"):
    # Open the configurations file
    print("Parsing provided configurations file... ")
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Perform deployment of headnode
    # rest all will be handled by headnode
    print("Deploying head node ... ")
    head_ip = deploy_headnode(name_prefix=f"UZ-{identifier}", configs = configs["instances"]["headnode"])
    print(f"Head node deployed at {head_ip} ...")
    
    # Obtain the swarm token
    # docker swarm join-token manager -q
    print("\nDeploying worker nodes ... ")
    worker_ips = launch_workernodes(name_prefix=f"UZ-{identifier}", num_nodes=configs["instances"]["workernodes"]["numworkers"], head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"])


if __name__ == "__main__":
    fire.Fire({
        "--full": full_deployment,
        "--add-node": add_workernode,
        "--del-node": del_workernode,
    })