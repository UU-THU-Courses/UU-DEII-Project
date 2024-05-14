import os
import pulsar
import argparse


def write_dict_to_file(str_dict, output_path):
    for key in str_dict:
        with open(f"{output_path}/out-{key}.txt", "a") as f:
            # Apply uppercase to the message
            # and write it to output file
            f.write(str_dict[key])


def consumer_process(pulsar_addr, pulsar_port, topic, cid, output_path):
    # Create a pulsar client by supplying ip address and port
    client = pulsar.Client(f"pulsar://{pulsar_addr}:{pulsar_port}")

    # Subscribe to a topic and subscription
    consumer = client.subscribe(topic=topic, 
                                subscription_name=f"sub-0",
                                consumer_type=pulsar.ConsumerType.KeyShared
                            )
    msg_counter = 0
    str_dict = dict()

    while True:
        try:
            msg = consumer.receive(timeout_millis = 300_000)
        except:
            # A timeout has occured apply the exit logic
            write_dict_to_file(str_dict, output_path)
            # Reset the accumulated strings
            str_dict = dict()
            break
        
        # Accumulate the messages received from broker
        try:

            # Append new word to the accumulated 
            # string with correct ordering key
            if msg.ordering_key() not in str_dict:
                print(f"Received ID : {msg.ordering_key()}", flush=True)
                str_dict[msg.ordering_key()] = ""
            
            str_dict[msg.ordering_key()] += msg.data().decode("utf-8").upper() + " "

            # Acknowledge for receiving the message
            consumer.acknowledge(msg)

            # Updated message counter
            msg_counter += 1

        except:
            print("Sending negative ACK!", flush=True)
            consumer.negative_acknowledge(msg)

        # Write to file every 10_000 words.
        if msg_counter % 10_000 == 0:
            print("\n\n--------------------------------------\n\n")
            # write to the dictionary to file
            write_dict_to_file(str_dict, output_path)
            # Reset the accumulated strings
            str_dict = dict()

    # Destroy pulsar client
    client.close()

if __name__=="__main__":
    parser = argparse.ArgumentParser(
                    prog="Consumer process",
                    description="Consumes whatever is produced by a producer",
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
        "--cid", 
        type=int,
        help="Consumer ID"
    )
    parser.add_argument(
        "--topic", 
        type=str,
        default="DEtopic",
        help="The topic that the consumer should subscribe to."
    )
    parser.add_argument(
        "--output_path", 
        type=str,
        default="output_data/",
        help="Path to the input data files."
    )
    args = parser.parse_args()

    # Log message for debugging
    print(f"ADDR is: {args.address}")
    print(f"PORT is: {args.port}")

    # Create output folder if does not exist
    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    consumer_process(pulsar_addr=args.address, pulsar_port=args.port, topic=args.topic, cid=args.cid, output_path=args.output_path)