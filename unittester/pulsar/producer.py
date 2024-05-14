import os, os.path
import pulsar
import argparse

minibatch_size = 10_000

def producer_process(pulsar_addr, pulsar_port, topic, pid, n_producers, input_path):
    # Create a pulsar client by supplying ip address and port
    client = pulsar.Client(f"pulsar://{pulsar_addr}:{pulsar_port}")

    # Create a producer on the topic that consumer can subscribe to
    producer = client.create_producer(
                                topic=topic, 
                                batching_type=pulsar.BatchingType.KeyBased,
                            ) 

    # Process all files in a tiled manner
    total_files = len([name for name in os.listdir(input_path) if os.path.isfile(f"{input_path}/{name}")])
    
    print(f"Producer: {pid} of {n_producers}. Total files in {input_path} are: {total_files}")

    for i in range(pid-1, total_files, n_producers):
        print(f"Producer: {pid} of {n_producers}. Reading file id: {i}")

        with open(f"{input_path}/data-{pid-1}.txt", "r") as f:
            # Send a message to consumer
            file_content = f.read()

        # Send data on per word basis
        for word in file_content.split():
            producer.send(content=(word).encode("utf-8"), ordering_key=f"DocumentKey-{i}", partition_key=f"DocumentKey-{i}")

    # Destroy pulsar producer and client
    producer.flush()
    producer.close()
    client.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(
                prog="Producer process",
                description="Produces whatever needs to be produced",
                epilog="~~~~")
    
    # Setup ip addresss as an argument
    parser.add_argument(
        "--address", 
        type=str,
        default="localhost",
        help="ip address of pulsar deployment"
    )
    parser.add_argument(
        "--port", 
        type=int,
        default=6650,
        help="port number of pulsar deployment"
    )
    parser.add_argument(
        "--pid", 
        type=int,
        help="Producer ID"
    )
    parser.add_argument(
        "--topic", 
        type=str,
        default="DEtopic",
        help="The topic that the consumer should subscribe to."
    )
    parser.add_argument(
        "--data_path", 
        type=str,
        default="input_data/",
        help="Path to the input data files."
    )
    parser.add_argument(
        "--n_producers", 
        type=int,
        default=1,
        help="Number of producers."
    )
    
    args = parser.parse_args()

    # Log message for debugging
    print(f"ADDR is: {args.address}")
    print(f"PORT is: {args.port}")

    producer_process(pulsar_addr=args.address, pulsar_port=args.port, topic=args.topic, pid=args.pid, input_path=args.data_path, n_producers=args.n_producers)