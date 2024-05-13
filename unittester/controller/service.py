# import docker
from consumer import Consumer
from producer import Producer


CONS_QUEUE = "task_queue"
PROD_QUEUE = "result_queue"

consumer = Consumer()
producer = Producer()

# client = docker.from_env()

def callback_func(ch, method, properties, body):
    received_msg = body.decode()
    received_msg += "-append-from-consumer"
    producer.publish(message=received_msg, queue=PROD_QUEUE)

if __name__=="__main__":
    consumer.declare_queue(CONS_QUEUE)
    producer.declare_queue(PROD_QUEUE)

    # Start Consuming the queue
    consumer.consume(callback=callback_func, queue=CONS_QUEUE)