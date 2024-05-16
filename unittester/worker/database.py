from pymongo import MongoClient
from datetime import datetime


class CustomMongoDB:
    def __init__(self, username="custom_admin", password="custom_passw", host="mongo", port=27017, summary_database="results") -> None:
        self.CONNECTION_STRING = f"mongodb://{username}:{password}@{host}:{port}/{summary_database}?authSource=admin"
        self.client = MongoClient(self.CONNECTION_STRING)
        self.summary_database = summary_database
        
    def insert_summary(self, reponame, repolink, tests, errors, skipped, failures, runtime):
        dbname = self.client[self.summary_database]
        collection_name = dbname["summary"]
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
