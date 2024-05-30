import pika, time

class Producer:
    def __init__(self, host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue="gitrepos") -> None:
        self.connection_params = pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username, password), heartbeat=1200)
        self.connection = None
        self.channel = None
        while True:
            try: 
                self.reconnect()
                break
            except:
                # Sleep for 60 seconds, probably the 
                # Rabbit service is not up yet.
                time.sleep(60)
        
        # Declare a queue with specified queue name
        self.queue = queue
        self.channel.queue_declare(queue=queue, durable=True)

    def reconnect(self):
        if self.connection is None or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self.connection_params)
            self.channel = self.connection.channel()

    def publish(self, message):
        self.channel.basic_publish(
            exchange="",
            routing_key=self.queue,
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