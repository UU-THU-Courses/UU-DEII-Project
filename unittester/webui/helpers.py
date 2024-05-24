import pika
import requests
import time
from pymongo import MongoClient
from bson.objectid import ObjectId

class MongodbReader:
    def __init__(self, username="custom_admin", password="custom_passw", host="mongo", port=27017, summary_database="results") -> None:
        self.CONNECTION_STRING = f"mongodb://{username}:{password}@{host}:{port}/{summary_database}?authSource=admin"
        self.client = MongoClient(self.CONNECTION_STRING)
        self.summary_database = summary_database
 
    def fetch_repositories(self, filter=None):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        documents = collection_name.find(filter=filter, projection={"_id": 0})
        response = []
        for document in documents:
            response += [dict(document)]
        return response
 
    def fetch_summary(self):
        dbname = self.client[self.summary_database]
        collection_name = dbname["summary"]
        documents = collection_name.find(projection={"_id": 0})
        response = []
        for document in documents:
            response += [dict(document)]
            response[-1]["runtime"] = round(response[-1]["runtime"], 2)
        return response
 
    def fetch_failures(self):
        dbname = self.client[self.summary_database]
        collection_name = dbname["maven_error"]
        documents = collection_name.find(projection={"_id": 1, "reponame": 1, "repolink": 1})
        response = []
        for document in documents:
            response += [dict(document)]
        return response

    def fetch_exception(self, record_id):
        dbname = self.client[self.summary_database]
        collection_name = dbname["maven_error"]
        document = collection_name.find_one(filter={"_id": ObjectId(record_id)}, projection={"_id": 0, "reponame": 1, "repolink": 1, "exception": 1})
        return dict(document)

    def cleanup(self):
        self.client.close()
    
    def __del__(self):
        self.cleanup()

def rabbit_queue_len(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue="gitrepos") -> None:
    connection = None
    channel = None
    while True:
        try: 
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=pika.PlainCredentials(username, password), heartbeat=1200))
            channel = connection.channel()
            break
        except:
            # Sleep for 60 seconds, probably the Rabbit 
            # service is not up yet.
            time.sleep(60)
    
    # Declare a queue with specified queue name
    queue_response = channel.queue_declare(queue=queue, durable=True, passive=True)
    if queue_response: print(queue_response.method.message_count)
    
    if channel: channel.close()
    if connection: connection.close()

    del channel, connection
    
    return queue_response.method.message_count

def generate_summary(mongo_reader):
    response_dict = {
        "n_process": 0,
        "n_failure": 0,
        "n_success": 0,
        "queue_len": 0 
    }

    try:    
        n_process = len(mongo_reader.fetch_repositories(filter = {"status": "Processing"}))
        n_failure = len(mongo_reader.fetch_repositories(filter = {"status": "Failed"}))
        n_success = len(mongo_reader.fetch_repositories(filter = {"status": "Success"}))
        response_dict["n_process"] += n_process
        response_dict["n_failure"] += n_failure
        response_dict["n_success"] += n_success
    except:
        pass

    try:
        queue_len = rabbit_queue_len()
        response_dict["queue_len"] += queue_len
    except:
        pass

    return response_dict

def fetch_cluster_info():
    cluster_info = dict()
    response = requests.get(f"http://localhost:5200/summary", timeout = 180)
    status_code = response.status_code
    print(status_code)
    if status_code == 200: cluster_info = response.json()
    return cluster_info    

# if __name__ == "__main__":
#     mongo_reader = MongodbReader(host="localhost")
#     summary = generate_summary(mongo_reader)
#     print(summary, flush=True)
#     mongo_reader.cleanup()
#     del mongo_reader
    
#     import threading
#     print(threading.enumerate())
