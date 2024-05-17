import os
import shutil
import subprocess

def generate_keypair(keypath, keyname):
    """A cryptographic module to generate RSA keypair."""
    shutil.rmtree(keypath)
    os.makedirs(keypath, exist_ok=True)
    
    run_cmd = f'ssh-keygen -q -t rsa -N "" -f {keypath}/{keyname}'
    subprocess.call(run_cmd, shell = True)

    return read_public_key(keypath, keyname)

def read_public_key(keypath, keyname):    
    """A helper module to read the generated public key"""
    with open(f"{keypath}/{keyname}.pub", "r") as keyfile:
        ssh_key = keyfile.read().strip()

    return ssh_key

if __name__ == "__main__":
    generate_keypair("__temp__")
