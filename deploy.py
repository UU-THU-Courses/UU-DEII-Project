import fire
import random, subprocess, argparse

from unittester.utils.requisition import create_instance
from unittester.utils.configs import parse_configs

MAX_ATTEMPTS = 10

def deploy_headnode(name_prefix, configs):
    """A module to create the headnode and send config files."""
    
    # Create the headnode and obtain ip address
    ip_addr = create_instance(name=f"{name_prefix}-headnode", configs=configs)

    return ip_addr

def add_workernode(num_nodes = 1, head_ip = None, configs = "configs/deploy-cfg.yaml"):
    pass

def del_workernode(node_ip):
    pass

def full_deployment(config_file = "configs/deploy-cfg.yaml"):
    # Open the configurations file
    configs = parse_configs(config_path=config_file)

    # Produce a random identifier
    identifier = random.randint(1000,9999)

    # Perform deployment of headnode
    # rest all will be handled by headnode
    head_ip = deploy_headnode(name_prefix=f"UZ-{identifier}", configs = configs["instances"]["headnode"])


if __name__ == "__main__":
    fire.Fire({
        "--full": full_deployment,
        "--add-node": add_workernode,
        "--del-node": del_workernode,
    })