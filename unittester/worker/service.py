# import docker
import time
import argparse
import subprocess

from consolidate import process_reports

from consumer import Consumer
from producer import Producer

CONS_QUEUE = "gitrepos"
PROD_QUEUE = "outputs"

def rabbit_callback_func(ch, method, properties, body):
    global prod
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    received_msg = body.decode()
    run_command = rf"bash unittest.sh {received_msg} /testRepo"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports("/testRepo/")    
    prod.publish(message=results_dict, queue=PROD_QUEUE)

def pulsar_callback_func(message):
    global prod
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    run_command = rf"bash unittest.sh {message} /testRepo"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports("/testRepo/")
    prod.publish(message=results_dict)

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
    global cons, prod
    if args.pulsar:
        cons = Consumer(host="pulsar", port=6650, topic=CONS_QUEUE)
        prod = Producer(host="pulsar", port=6650, topic=PROD_QUEUE)
        cons.consume(callback=pulsar_callback_func, topic=CONS_QUEUE)
    else:        
        cons = Consumer()
        prod = Producer()
        cons.declare_queue(CONS_QUEUE)
        prod.declare_queue(PROD_QUEUE)
        cons.consume(callback=rabbit_callback_func, queue=CONS_QUEUE)

