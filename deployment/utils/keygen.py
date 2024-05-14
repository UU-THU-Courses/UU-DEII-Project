import os
import shutil
import subprocess

def generate_keypair(keypath="temp_keypairs"):
    """A cryptographic module to generate RSA keypair."""
    shutil.rmtree(keypath)
    os.makedirs(keypath, exist_ok=True)
    
    run_cmd = f'ssh-keygen -q -t rsa -N "" -f {keypath}/id_rsa'
    subprocess.call(run_cmd, shell = True)
    
    with open(f"{keypath}/id_rsa.pub", "r") as keyfile:
        ssh_key = keyfile.read().strip()

    return ssh_key

if __name__ == "__main__":
    generate_keypair("__temp__")
