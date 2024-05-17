import time
import argparse
import json
from os import environ as env
from search_github import GitHubAPI

# Declare few paths
MAX_PAGES   = 200
PER_PAGE    = 100
GIT_ACCESS_TOKEN = env["GIT_ACCESS_TOKEN"]

def rabbit_crawler(producer_queue):
    # Create a producer instance
    from rabbit_producer import Producer
    prod = Producer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue=producer_queue)

    api_search = GitHubAPI(
        access_token=GIT_ACCESS_TOKEN,
        results_per_page=PER_PAGE,
    )

    # Search github using API for valid 
    # repositories, using batches
    for page in range(1, MAX_PAGES+1):
        discovered_repos = api_search.perform_search(page_num=page)

        # Go through each discovered repository
        # and validate that it contains pom.xml
        for item in discovered_repos:
            if api_search.validity_check(url = item["url"]):
                prod.publish(message=json.dumps(obj = item))

        # Sleep between batches
        if (page * PER_PAGE) % 1000 == 0: time.sleep(60)

    del prod

def pulsar_crawler(producer_queue):
    # Create a producer instance
    from pulsar_producer import Producer
    prod = Producer(host="pulsar", port=6650, topic=producer_queue)

    api_search = GitHubAPI(
        access_token=GIT_ACCESS_TOKEN,
        results_per_page=PER_PAGE,
    )

    # Search github using API for valid 
    # repositories, using batches
    for page in range(1, MAX_PAGES+1):
        discovered_repos = api_search.perform_search(page_num=page)

        # Go through each discovered repository
        # and validate that it contains pom.xml
        for item in discovered_repos:
            if api_search.validity_check(url = item["url"]):
                prod.publish(message=json.dumps(obj = item))

        # Sleep between batches
        if (page * PER_PAGE) % 1000 == 0: time.sleep(60)

    del prod

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pulsar",
        required=False,
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--target-queue",
        type=str,
        required=False,
        default="gitrepos",
    )
    args = parser.parse_args()
    
    if args.pulsar:
        pulsar_crawler(args.target_queue)
    else:
        rabbit_crawler(args.target_queue)