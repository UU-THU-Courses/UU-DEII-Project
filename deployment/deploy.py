import os
import fire
import random
import subprocess

from utils.requisition import create_instance
from utils.configs import parse_configs, write_configs
#from utils.keygen import generate_keypair

MAX_ATTEMPTS = 10

def deploy_headnode(name_prefix, configs, ssh_key):
    """A module to create the headnode and send config files."""

    cloud_cfg = parse_configs(config_path=configs["instance_configs"])
    configs["instance_configs"] = "__temp_dir__/temp_headnode_cfg.yaml"
    
    # Append new key for all users
    for user in cloud_cfg["users"]:
        user["ssh_authorized_keys"].append(ssh_key)

    os.makedirs("__temp_dir__", exist_ok=True)
    write_configs(configs["instance_configs"], cloud_cfg)

    # Prepend the head comment: #cloud-config 
    # to newly created yaml file
    with open(configs["instance_configs"], "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write("#cloud-config" + "\n\n" + content)

    # Create the headnode and obtain ip address
    ip_addr = create_instance(name=f"{name_prefix}-headnode", configs=configs)

    return ip_addr

def launch_workernodes(name_prefix, num_nodes, head_ip, configs, ssh_key):
    # Update cloud configurations in order to write
    # the head ip address to a temporary file at
    # worker node
    
    cloud_cfg = parse_configs(config_path=configs["instance_configs"])
    configs["instance_configs"] = "__temp_dir__/temp_worknode_cfg.yaml"
    
    # Append new key for all users
    for user in cloud_cfg["users"]:
        user["ssh_authorized_keys"].append(ssh_key)
    
    # Write head ip to a file
    cloud_cfg["write_files"] = [{
        "content": f"{head_ip}",
        "path": "/HEAD-IP.txt",
        "permissions": "0644",
    }]
    os.makedirs("__temp_dir__", exist_ok=True)
    write_configs(configs["instance_configs"], cloud_cfg)

    # Prepend the head comment: #cloud-config 
    # to newly created yaml file
    with open(configs["instance_configs"], "r+") as f:
        content = f.read()
        f.seek(0, 0)
        f.write("#cloud-config" + "\n\n" + content)

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
    print("\nDeploying worker nodes ... ")
    worker_ips = launch_workernodes(name_prefix=f"UZ-{identifier}", num_nodes=num_nodes, head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"])

def full_deployment(config_file = "configs/deploy-cfg.yaml"):
    # Open the configurations file
    print("Parsing provided configurations file... ")
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Generate a new private/public keypair
    os.makedirs("temp_keypairs", exist_ok=True)
    # generate_keypair(keypath="temp_keypairs")
    run_cmd = f'ssh-keygen -q -t rsa -N "" -f temp_keypairs/id_rsa'
    subprocess.call(run_cmd, shell = True)
    with open("temp_keypairs/id_rsa.pub", "r") as keyfile:
        ssh_key = keyfile.read().strip()

    # Perform deployment of headnode
    # rest all will be handled by headnode
    print("Deploying head node ... ")
    head_ip = deploy_headnode(name_prefix=f"UZ-{identifier}", configs=configs["instances"]["headnode"], ssh_key=ssh_key)
    print(f"Head node deployed at {head_ip} ...")
    
    # Obtain the swarm token
    # docker swarm join-token manager -q
    print("\nDeploying worker nodes ... ")
    worker_ips = launch_workernodes(name_prefix=f"UZ-{identifier}", num_nodes=configs["instances"]["workernodes"]["numworkers"], head_ip=head_ip, configs=configs["instances"]["workernodes"]["workercfgs"], ssh_key=ssh_key)


if __name__ == "__main__":
    fire.Fire({
        "--full": full_deployment,
        "--add-node": add_workernode,
        "--del-node": del_workernode,
    })