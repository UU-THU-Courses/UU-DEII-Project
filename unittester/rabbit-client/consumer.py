import pika, time

class Consumer:
    def __init__(self, host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", exchange=None, exchange_type=None, queue=None) -> None:
        self.connection = None
        self.channel = None
        while True:
            try: 
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username, password)))
                self.channel = self.connection.channel()
                break
            except:
                # Sleep for 60 seconds, probably the Rabbit 
                # service is not up yet.
                time.sleep(60)
        
        # Declare requested exchange and
        # queue
        self.exchange = exchange
        self.queue = queue
        if self.exchange: self.channel.exchange_declare(exchange=exchange, exchange_type=exchange_type)
        if self.queue == "":
            result = self.channel.queue_declare(queue=self.queue, exclusive=True)
            self.queue = result.method.queue
        else:
            self.channel.queue_declare(queue=self.queue, durable=True)
        
        # Bind exchange to the queue
        self.channel.queue_bind(exchange=self.exchange, queue=self.queue)

    def consume(self, callback, queue):
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=callback,
            auto_ack=True,
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
