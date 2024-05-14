import time
import argparse
from producer import Producer

PROD_QUEUE = "gitrepos"

# Declare few paths
TEMP_PATHS = [
    "https://github.com/ZHENFENG13/My-Blog.git",
    "https://github.com/ZHENFENG13/My-Blog.git",
    "https://github.com/ZHENFENG13/My-Blog.git"
]

def rabbit_crawler():
    # Create a producer instance
    prod = Producer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq")
    prod.declare_queue(queue=PROD_QUEUE)

    for i in range(100):
        for gitpath in TEMP_PATHS:
            prod.publish(message=gitpath, queue=PROD_QUEUE)

    del prod
    time.sleep(600)

def pulsar_crawler():
    prod = Producer(host="pulsar", port=6650, topic=PROD_QUEUE)
    
    for i in range(100):
        for gitpath in TEMP_PATHS:
            prod.publish(message=gitpath) 

    del prod
    time.sleep(600)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pulsar",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()
    
    if args.pulsar:
        pulsar_crawler()
    else:
        rabbit_crawler()