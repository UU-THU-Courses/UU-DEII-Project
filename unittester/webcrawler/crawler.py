import time
import argparse
import json
from os import environ as env
from search_github import GitHubAPI

# Declare few paths
MAX_PAGES   = 10
PER_PAGE    = 100

with open("/crawlerdata/GITHUB_ACCESS_TOKEN.txt", "r") as f:
    GITHUB_ACCESS_TOKEN = f.read().strip()


def wait_search_limit_reset(api_search):
    """Wait 1 minute for search limit to reset"""
    while True:
        rate_limit = api_search.check_rate_limit()["resources"]["search"]
        if rate_limit["limit"] > rate_limit["used"]: 
            break
        time.sleep(60)

def wait_core_limit_reset(api_search):
    """Wait 1 hour for the core limit to reset"""
    while True:
        rate_limit = api_search.check_rate_limit()["resources"]["core"]
        if rate_limit["limit"] > rate_limit["used"]: 
            break
        time.sleep(3600)

def rabbit_crawler(producer_queue, replica, max_replicas):
    # Create a producer instance
    from rabbit_producer import Producer
    prod = Producer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue=producer_queue)

    api_search = GitHubAPI(
        access_token=GITHUB_ACCESS_TOKEN,
        results_per_page=PER_PAGE,
    )

    for sortby in [None, "stars", "forks", "updated"]:
        for sortorder in ["desc", "asc"]:
            # Search github using API for valid repositories, using batches
            for page in range(replica-1, MAX_PAGES+1, max_replicas):
                try:
                    wait_search_limit_reset(api_search)
                    discovered_repos = api_search.perform_search(page_num=page, sort=sortby, order=sortorder)

                    # Go through each discovered repository
                    # and validate that it contains pom.xml
                    for item in discovered_repos:
                        wait_core_limit_reset(api_search)
                        if api_search.validity_check(url = item["url"]):
                            prod.publish(message=json.dumps(obj = item))

                except Exception as e:
                    pass

    del prod

def pulsar_crawler(producer_queue, replica, max_replicas):
    # Create a producer instance
    from pulsar_producer import Producer
    prod = Producer(host="pulsar", port=6650, topic=producer_queue)

    api_search = GitHubAPI(
        access_token=GITHUB_ACCESS_TOKEN,
        results_per_page=PER_PAGE,
    )

    # Search github using API for valid 
    # repositories, using batches
    for page in range(replica, MAX_PAGES+1, max_replicas):
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

    env_replica = env["REPLICA"]
    env_max_rep = env["MAX_REPLICA"]
    
    replica = int(env_replica) if env_replica.isnumeric() else 1
    max_replicas = int(env_max_rep) if env_max_rep.isnumeric() else 1

    print(f"I am replica: {replica} of {max_replicas}.")

    if args.pulsar:
        pulsar_crawler(args.target_queue, replica, max_replicas)
    else:
        rabbit_crawler(args.target_queue, replica, max_replicas)