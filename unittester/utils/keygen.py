from os import chmod
from OpenSSL import crypto

def generate_keypair(private_path, public_path):
    """A cryptographic module to generate RSA keypair."""

    # Generate an 2048 bit RSA private key
    # and write the private key to a file
    # key = RSA.generate(2048)
    # with open(private_path, "wb") as keyfile:
    #     chmod(private_path, 0o600)
    #     keyfile.write(key.exportKey("PEM"))
    
    # Generate the public key corresponding
    # to private key and write key to a file
    # pubkey = key.publickey()
    # with open(public_path, "wb") as keyfile:
    #     keyfile.writable(pubkey.exportKey("OpenSSH"))

    # Use OpenSSL wrapper to generate the keys
    # Generate an 3072 bit RSA private key
    private_key = crypto.PKey()
    private_key.generate_key(crypto.TYPE_RSA, 3072)
    ## ssh-keygen -q -t rsa -N "" -f "./t1_rsa"
    
    # Write the private key to a file
    with open(private_path, "wb") as keyfile:
        # chmod(private_path, 0o400)
        keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key))
    
    # Generate the public key corresponding
    # to private key and write key to a file
    with open(public_path, "wb") as keyfile:
        keyfile.write(crypto.dump_publickey(crypto.FILETYPE_PEM, private_key))


if __name__ == "__main__":
    generate_keypair("__temp/pr_key.pem", "__temp/pb_key")
