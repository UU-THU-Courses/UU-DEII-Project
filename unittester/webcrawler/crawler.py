import time
from producer import Producer

PROD_QUEUE = "task_queue"

# Declare few paths
TEMP_PATHS = [
    "Test-1",
    "Test-2",
    "Test-3"
]

def crawl_github():
    # Create a producer instance
    prod = Producer()
    prod.declare_queue(queue=PROD_QUEUE)

    for i in range(10000):
        for gitpath in TEMP_PATHS:
            prod.publish(message=gitpath, queue=PROD_QUEUE)

    time.sleep(600)

if __name__ == "__main__":
    crawl_github()