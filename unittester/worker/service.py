# import docker
import time
import shutil
import argparse
import subprocess

from consolidate import process_reports
from consumer import Consumer
from producer import Producer

CONS_QUEUE = "gitrepos"
PROD_QUEUE = "outputs"

def rabbit_callback_func(ch, method, properties, body):
    global prod, repo_download_path
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    received_msg = body.decode()
    run_command = rf"bash unittest.sh {received_msg} /testRepo"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports("/testRepo/")    
    prod.publish(message=results_dict, queue=PROD_QUEUE)
    # Perform clean up of temporary paths
    shutil.rmtree(repo_download_path)

def pulsar_callback_func(message):
    global prod, repo_download_path
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    run_command = rf"bash unittest.sh {message} {repo_download_path}"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports("/testRepo/target/surefire-reports")
    prod.publish(message=results_dict.__str__())
    # Perform clean up of temporary paths
    shutil.rmtree(repo_download_path)
    return True

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pulsar",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    
    # Consumer messages
    global cons, prod, repo_download_path
    repo_download_path = "/testRepo"
    
    if args.pulsar:
        cons = Consumer(host="pulsar", port=6650, topic=CONS_QUEUE)
        prod = Producer(host="pulsar", port=6650, topic=PROD_QUEUE)
        cons.consume(callback=pulsar_callback_func)
    else:        
        cons = Consumer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", exchange=CONS_QUEUE, exchange_type="topic", queue="")
        prod = Producer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", exchange=PROD_QUEUE, exchange_type="topic", queue=None)
        cons.consume(callback=rabbit_callback_func, queue=CONS_QUEUE)

