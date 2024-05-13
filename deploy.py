import fire
import time, subprocess, argparse

from unittester.utils.requisition import create_instance
from unittester.utils.configs import parse_configs

MAX_ATTEMPTS = 10

# def send_files(username, ip_addr, ssh_secretkey_path, n_attempts = 0):
#     try:
#         subprocess.run([
#             "scp", "-q", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-i", ssh_secretkey_path, "-r", "configs", f"{username}@{ip_addr}:/home/{username}/"], check=True)
#     except:
#         time.sleep(120)
#         if n_attempts < MAX_ATTEMPTS: send_files(ip_addr, n_attempts+1)

def deploy_headnode(configs = None):
    """A module to create the headnode and send config files."""
    
    # Create the headnode and obtain ip address
    ip_addr = create_instance(name="t1-headnode", configs=configs)

def add_workernode(num_nodes = 1, head_ip = None, configs = "configs/deploy-cfg.yaml"):
    pass

def del_workernode(node_ip):
    pass

def full_deployment(config_file = "configs/deploy-cfg.yaml"):
    # Open the configurations file
    configs = parse_configs(config_path=config_file)

    # Perform deployment of headnode
    # rest all will be handled by headnode
    deploy_headnode(configs = configs["instances"]["headnode"])


if __name__ == "__main__":
    fire.Fire({
        "--full": full_deployment,
        "--add-node": add_workernode,
        "--del-node": del_workernode,
    })