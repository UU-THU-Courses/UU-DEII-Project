from pymongo import MongoClient

class MongodbReader:
    def __init__(self, username="custom_admin", password="custom_passw", host="mongo", port=27017, summary_database="results") -> None:
        self.CONNECTION_STRING = f"mongodb://{username}:{password}@{host}:{port}/{summary_database}?authSource=admin"
        self.client = MongoClient(self.CONNECTION_STRING)
        self.summary_database = summary_database
 
    def fetch_repositories(self):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        documents = collection_name.find(projection={"_id": 0})
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

    def __del__(self):
        self.client.close()

# if __name__ == "__main__":
#     mongo_reader = MongodbReader(host="localhost")
#     print(mongo_reader.fetch_repositories())
#     del mongo_reader
#     #exit(0)