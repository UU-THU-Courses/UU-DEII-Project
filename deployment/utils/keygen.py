from os import chmod
from OpenSSL import crypto
import subprocess

def generate_keypair(keypath, bits = 3072):
    """A cryptographic module to generate RSA keypair."""
    # Use OpenSSL wrapper to generate the keys
    # Generate an 3072 bit RSA private key
    private_key = crypto.PKey()
    private_key.generate_key(crypto.TYPE_RSA, 3072)
    
    # Write the private key to a file
    private_keypath = keypath+"/privatekey"
    with open(private_keypath, "wb") as keyfile:
        # chmod(private_path, 0o400)
        keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))
    
    # Generate equivalent public key
    # run_cmd = f'ssh-keygen -q -t rsa -N "" -f {private_keypath}'
    # subprocess.call(run_cmd, shell = True)

if __name__ == "__main__":
    # os.makedirs("temp_keypairs", exist_ok=True)
    generate_keypair("__temp__")
