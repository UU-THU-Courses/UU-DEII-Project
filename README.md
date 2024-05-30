# UU-DEII-Project
A project for the course of Data Engineering II at Uppsala University. The project implements an automated pipeline to search, download and run unit tests on GitHub repositories with maven system.

## To Run:
In order to run the code follow these steps:

* Create a client virtual machine on SSC cloud (any flavor would do, recommended: ssc-medium)
* Clone the repository from above link or copy this directory onto client virtual machine.
* Navigate to path ```project/deployment```.
* Run ```setup.sh``` file in order to install various required dependencies.
* Open the configurations file located at path ```configs/deploy-cfg.yaml``` and make following changes:
    * Add your github authentication token in the empty field.
    * [Optional] Add public keys you want associated with new nodes as a list to ssh_authorized_keys.
    * [Optional] Modify the head-node configs if needed.
    * [Optional] Modify worker-node configs if needed including number of worker-nodes to launch.
* Make sure you have sourced the OpenStack RC file before proceeding.
* Once config file is to your satisfaction, simply run ```deploy.sh``` script to deploy the whole stack.
* To add more worker nodes run: ```python3 deploy.py --add-nodes --num_nodes {count}```
* To delete worker nodes run: ```python3 deploy.py --del-nodes --num_nodes {count} --head_ip {ip_of_headnode}```
* Once the stack is up and running (wait few minutes for deployment) assign the headnode a floating ip address and navigate to ```http://ip-address:5100``` to browse the WebUI and see status of application and cluster.