import time
import argparse

# Declare few paths
TEMP_PATHS = [
    "https://github.com/ZHENFENG13/My-Blog.git",
    "https://github.com/ZHENFENG13/My-Blog.git",
    "https://github.com/ZHENFENG13/My-Blog.git"
]

def rabbit_crawler(producer_queue):
    # Create a producer instance
    from rabbit_producer import Producer
    prod = Producer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue=producer_queue)
    
    for i in range(10):
        for gitpath in TEMP_PATHS:
            prod.publish(message=gitpath)

    del prod

def pulsar_crawler(producer_queue):
    # Create a producer instance
    from pulsar_producer import Producer
    prod = Producer(host="pulsar", port=6650, topic=producer_queue)
    
    for i in range(10):
        for gitpath in TEMP_PATHS:
            prod.publish(message=gitpath) 

    del prod

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pulsar",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--target-queue",
        type=str,
        required=False,
        default="gitrepos",
    )
    args = parser.parse_args()
    
    if args.pulsar:
        pulsar_crawler(args.target_queue)
    else:
        rabbit_crawler(args.target_queue)