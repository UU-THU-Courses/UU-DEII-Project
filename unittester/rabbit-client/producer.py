import pika, time

class Producer:
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
        if self.queue: self.channel.queue_declare(queue=queue, durable=True)

    def publish(self, message, routing_key):
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent
            )
        )
    
    def __del__(self):
        if self.connection: self.connection.close()

if __name__ == "__main__":
    prod = Producer()
    prod.declare_queue(queue="task_queue")
    prod.publish("TEST-MESSAGE-1", "task_queue")
    prod.publish("TEST-MESSAGE-2", "task_queue")
    prod.publish("TEST-MESSAGE-3", "task_queue")
    prod.publish("TEST-MESSAGE-4", "task_queue")