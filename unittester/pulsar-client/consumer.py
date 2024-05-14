import time
import pulsar

class Consumer:
    def __init__(self, host="pulsar", port=6650, topic = "gitrepos") -> None:
        self.client = None
        self.consumer = None
        while True:
            try:     
                # Create a pulsar client by supplying ip address and port
                self.client = pulsar.Client(f"pulsar://{host}:{port}")
                
                # Subscribe to a topic and subscription
                self.consumer = self.client.subscribe(
                    topic=topic,
                    subscription_name=f"sub-0",
                    consumer_type=pulsar.ConsumerType.KeyShared
                )

                # Success break out of loop
                break
            except:
                # Sleep for 60 seconds, probably the Pulsar 
                # service is not up yet.
                time.sleep(60)

    def consume(self, callback):
        while True:
            try:
                msg = self.consumer.receive(timeout_millis = 300_000)
            except:
                # A timeout has occured apply the exit logic
                break
            
            # Process the message received from broker
            try:
                # Run the callback message
                if callback(msg.data().decode()):
                    # Acknowledge for receiving the message
                    self.consumer.acknowledge(msg)
                else:
                    print("Sending negative ACK!", flush=True)
                    self.consumer.negative_acknowledge(msg)
            except:
                print("Sending negative ACK!", flush=True)
                self.consumer.negative_acknowledge(msg)

    def __del__(self):
        # Destroy pulsar consumer and client
        if self.consumer: self.consumer.close()
        if self.client: self.client.close()