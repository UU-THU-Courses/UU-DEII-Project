from pymongo import MongoClient

class MongodbReader:
    def __init__(self, username="custom_admin", password="custom_passw", host="mongo", port=27017, summary_database="results") -> None:
        self.CONNECTION_STRING = f"mongodb://{username}:{password}@{host}:{port}/{summary_database}?authSource=admin"
        self.client = MongoClient(self.CONNECTION_STRING)
        self.summary_database = summary_database
 
    def fetch_repositories(self):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        # if not collection_name.count_documents(filter={"reponame": reponame, "repolink": repolink}, limit = 1): return 0, None
        documents = collection_name.find(projection={"_id": 0})
        response = []
        for document in documents:
            response += [dict(document)]
        return response

    def __del__(self):
        self.client.close()

# if __name__ == "__main__":
#     mongo_reader = MongodbReader(host="localhost")
#     print(mongo_reader.fetch_repositories())
#     del mongo_reader
#     #exit(0)