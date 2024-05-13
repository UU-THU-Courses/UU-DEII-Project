import pika

class Consumer:
    def __init__(self, host="rabbit", port=5672, username="rabbitmq", password="rabbitmq") -> None:
        self.connection = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username, password)))
        self.channel = self.connection.channel()

    def declare_queue(self, queue, durable=True):
       self.channel.queue_declare(queue=queue, durable=durable)
    
    def consume(self, callback, queue):
        self.channel.basic_consume(
            queue=queue,
            auto_ack=True,
            on_message_callback=callback
        )
        self.channel.start_consuming()
    
    def __del__(self):
        if self.connection: self.connection.close()

if __name__ == "__main__":
    def callback_func(ch, method, properties, body):
        received_msg = body.decode()
        print(received_msg)

    consumer = Consumer(host="localhost")
    consumer.declare_queue("result_queue")

    # Start Consuming the queue
    consumer.consume(callback=callback_func, queue="result_queue")
