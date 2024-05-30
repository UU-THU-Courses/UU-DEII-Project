import pika, time

class Consumer:
    def __init__(self, host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue="gitrepos") -> None:
        self.connection_params = pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username, password), heartbeat=1200)
        # Declare a queue with specified queue name
        self.queue = queue
        self.connection = None
        self.channel = None
        while True:
            try: 
                self.reconnect()
                break
            except:
                # Sleep for 60 seconds, probably the Rabbit 
                # service is not up yet.
                time.sleep(60)

    def reconnect(self):
        if self.connection is None or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue, durable=True)
            self.channel.basic_qos(prefetch_count=1)

    def consume(self, callback):
        self.channel.basic_consume(
            queue=self.queue,
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
