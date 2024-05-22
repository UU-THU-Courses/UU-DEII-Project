import time, os, sys, re
from os import environ as env

from  novaclient import client
from keystoneauth1 import loading
from keystoneauth1 import session


def create_instance(name, configs, debug = False):

    # Setup configurations
    flavor                  = configs["instance_flavor"]
    private_net             = configs["private_network"]
    image_name              = configs["instance_source"]
    key_name                = configs["authorized_keys"]
    floating_ip_pool_name   = configs["floating_ip_pool"]
    floating_ip             = configs["floating_ip_addr"]
    cfg_file_path           = configs["instance_configs"]

    # Get OpenStack configruations from 
    # environment variables
    loader = loading.get_plugin_loader("password")
    auth = loader.load_from_options(
        auth_url=env["OS_AUTH_URL"],
        username=env["OS_USERNAME"],
        password=env["OS_PASSWORD"],
        project_name=env["OS_PROJECT_NAME"],
        project_domain_id=env["OS_PROJECT_DOMAIN_ID"],
        user_domain_name=env["OS_USER_DOMAIN_NAME"]
    )

    # Authorize the user and create a new
    # session using credentials obtained
    sess = session.Session(auth=auth)
    nova = client.Client("2.1", session=sess)
    if debug: print("User authorization completed.")

    # Setup instance relation information
    image = nova.glance.find_image(image_name)
    flavor = nova.flavors.find(name=flavor)

    # Create network configurations
    if private_net != None:
        net = nova.neutron.find_network(private_net)
        nics = [{"net-id": net.id}]
    else:
        sys.exit("private-net not defined.")

    # Check that configuration file is available
    #print("Path at terminal when executing this file")
    #print(os.getcwd() + "\n")
    #cfg_file_path =  os.getcwd()+"/cloud-cfg.txt"
    secgroups = ["default"]

    # Create requested number of instances
    if debug: print("Creating instances ... ")

    # For some weird reason file is not being
    # resued after one instance
    if os.path.isfile(cfg_file_path):
        userdata = open(cfg_file_path)
    else:
        sys.exit("cloud-cfg.txt is not in current working directory")

    # Create the requested instance
    instance = nova.servers.create(
        name=f"{name}", 
        image=image, 
        flavor=flavor, 
        key_name=key_name, 
        userdata=userdata, 
        nics=nics, 
        security_groups=secgroups
    )
    instance_status = instance.status

    if debug: print ("\nWaiting for 10 seconds ... ")
    
    time.sleep(10)

    # Check all instances have changed
    # their status from BUILD
    while instance_status == "BUILD":
        if debug: print (f"Instance: {instance.name} is in {instance_status} state, sleeping for 10 seconds more ...")
        time.sleep(10)
        instance = nova.servers.get(instance.id)
        instance_status = instance.status

    # Acquire ip address of the new instance
    instance_ip = get_ip_address(instance, private_net)

    if debug: print (f"Instance: {instance.name} is in {instance_status}  state with ip address: {instance_ip}")

    # Return the newly created instances
    return instance_ip

def get_ip_address(instance, private_net):
    # Check ip address of the instance
    ip_address = None
    for network in instance.networks[private_net]:
        if re.match("\d+\.\d+\.\d+\.\d+", network):
            ip_address = network
            break
    
    # Raise exception if no ip address allocated
    if ip_address is None:
        raise RuntimeError("No IP address assigned!")

    # Return the obtained ip-addresses
    return ip_address

def delete_instance(server_name):
    # Get OpenStack configruations from 
    # environment variables
    loader = loading.get_plugin_loader("password")
    auth = loader.load_from_options(
        auth_url=env["OS_AUTH_URL"],
        username=env["OS_USERNAME"],
        password=env["OS_PASSWORD"],
        project_name=env["OS_PROJECT_NAME"],
        project_domain_id=env["OS_PROJECT_DOMAIN_ID"],
        user_domain_name=env["OS_USER_DOMAIN_NAME"]
    )

    # Authorize the user and create a new
    # session using credentials obtained
    sess = session.Session(auth=auth)
    nova = client.Client("2.1", session=sess)

    # Find the server using its name since we
    # need its id to perform delete operation
    server_list = nova.servers.list(search_opts={"name": server_name})
    if len(server_list) > 0:
        nova.servers.delete(server_list[0].id)
    else:
        raise Exception(f"Unable to find a matching server with name: {server_name}")
