import time
import pulsar

class Producer:
    def __init__(self, host="pulsar", port=6650, topic = "gitrepos") -> None:
        while True:
            try:     
                # Create a pulsar client by supplying ip address and port
                self.client = pulsar.Client(f"pulsar://{host}:{port}")
                
                # Create a producer on the topic that consumer can subscribe to
                self.producer = self.client.create_producer(topic=topic) 

                # Success break out of loop
                break
            except:
                # Sleep for 60 seconds, probably the Pulsar 
                # service is not up yet.
                time.sleep(60)

    def publish(self, message):
        self.producer.send(content=(message).encode("utf-8"))

    def __del__(self):
        # Destroy pulsar producer and client
        if self.producer: 
            self.producer.flush()
            self.producer.close()
        if self.client: self.client.close()
