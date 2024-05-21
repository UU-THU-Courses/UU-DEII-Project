from pymongo import MongoClient
from datetime import datetime


class CustomMongoDB:
    def __init__(self, username="custom_admin", password="custom_passw", host="mongo", port=27017, summary_database="results") -> None:
        self.CONNECTION_STRING = f"mongodb://{username}:{password}@{host}:{port}/{summary_database}?authSource=admin"
        self.client = MongoClient(self.CONNECTION_STRING)
        self.summary_database = summary_database
        
    def insert_summary(self, reponame, repolink, tests, errors, skipped, failures, runtime, exception = ""):
        dbname = self.client[self.summary_database]
        collection_name = dbname["summary"]
        data_item = {
            "reponame": reponame,
            "repolink": repolink,
            "tests": tests,
            "errors": errors,
            "skipped": skipped,
            "failures": failures,
            "runtime": runtime,
            "exception": exception,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        collection_name.insert_one(data_item)
    
    def insert_gitrepo(self, reponame, repolink, visibility, topics, stargazers_count, language, status):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        data_item = {
            "reponame": reponame,
            "repolink": repolink,
            "visibility": visibility,
            "topics": topics,
            "stargazers": stargazers_count,
            "language": language,
            "status": status,
            "attempts": 1,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        collection_name.insert_one(data_item)
    
    def update_gitrepo(self, reponame, repolink, updates):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        data_query = {
            "reponame": reponame,
            "repolink": repolink,  
        }
        updates["datetime"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update = {
            "$set": updates
        }
        collection_name.update_one(data_query, update) 

    def insert_errors(self, reponame, repolink, exception):
        dbname = self.client[self.summary_database]
        collection_name = dbname["maven_error"]
        data_item = {
            "repo": reponame,
            "link": repolink,
            "exception": exception,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }        
        collection_name.insert_one(data_item)
    
    def insert_details(self, reponame, repolink, tests, errors, skipped, failures, runtime):
        dbname = self.client[self.summary_database]
        collection_name = dbname["test-details"]
        data_item = {
            "repo": reponame,
            "link": repolink,
            "tests": tests,
            "errors": errors,
            "skipped": skipped,
            "failures": failures,
            "runtime": runtime,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        collection_name.insert_one(data_item)
    
    def fetch_attempts_and_status(self, reponame, repolink):
        dbname = self.client[self.summary_database]
        collection_name = dbname["repositories"]
        if not collection_name.count_documents(filter={"reponame": reponame, "repolink": repolink}, limit = 1): return 0, None
        record = collection_name.find_one(filter={"reponame": reponame, "repolink": repolink}, projection={"_id": 0, "attempts": 1, "status": 1})
        return record["attempts"], record["status"]

    def __del__(self):
        self.client.close()

if __name__ == "__main__":   
    mongodb_obj = CustomMongoDB()
    mongodb_obj.insert_summary(
        reponame="repo1", 
        repolink="https://github.com/repo1", 
        tests=10, 
        errors=2, 
        skipped=2, 
        failures=2, 
        runtime=10,
    )
    mongodb_obj.insert_details(
        reponame="repo1", 
        repolink="https://github.com/repo1", 
        tests=10, 
        errors=2, 
        skipped=2, 
        failures=2, 
        runtime=10,
    )
