import os
import json
import shutil
import argparse
import subprocess

from consolidate import process_reports
from database import CustomMongoDB


def normal_processing(received_msg, mongo_db):
    return_status = ""
    try:
        # Build the command to call the script that
        # downloads git repo and runs maven tests
        run_command = rf"bash runtest.sh {received_msg['html_url']} /testRepo"
        subprocess.call(run_command, shell=True)
        
        # Process the results using the process
        # reports module in consolidate.py
        results_dict = process_reports(xmlpath=f"{repo_download_path}/target/surefire-reports")
        
        # Insert results to database only
        # it there is at least 1 test
        # that was run (fail / pass)
        if results_dict["tests"] > 0 or results_dict["exception"] != "":
            mongo_db.insert_summary(
                reponame=received_msg["reponame"],
                repolink=received_msg["html_url"],
                tests=results_dict["tests"],
                errors=results_dict["errors"],
                skipped=results_dict["skipped"],
                failures=results_dict["failures"],
                runtime=results_dict["runtime"],
                exception=results_dict["exception"]
            )
            return_status = "Success"
        else:
            console_file = f"{repo_download_path}/temp-console-output-file.txt"
            if os.path.isfile(console_file):
                with open(console_file, "r") as f:
                    console_log = f.read()
            else:
                console_log = "No console file exists... Some error downloading git repository?"
            # Insert error to the errors table
            mongo_db.insert_errors(
                reponame=received_msg["reponame"],
                repolink=received_msg["html_url"],
                exception=console_log
            )
            return_status = "Failed"

        # Perform clean up of temporary paths
        if os.path.exists(repo_download_path): shutil.rmtree(repo_download_path)
    
    except Exception as e:
        return_status = "Failed"
    
    return return_status

def rabbit_callback_func(channel, method, properties, body):
    global mongo_db, repo_download_path

    # Log the fetched repositories name and link
    # along with other attributes to database
    received_msg = json.loads(body.decode())

    # Fetch number of existing attempts
    # on the current repository
    attempts, status = mongo_db.fetch_attempts_and_status(reponame=received_msg["reponame"], repolink=received_msg["html_url"])

    if attempts == 0:
        # The record does not exist, create an entry
        # for current repo and then proceed as normal
        mongo_db.insert_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            topics=received_msg["topics"],
            visibility=received_msg["visibility"],
            stargazers_count=received_msg["stargazers_count"],
            language=received_msg["language"],
            status="Processing"
        )
        return_status = normal_processing(received_msg, mongo_db)
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": return_status}
        )
    elif attempts < 10 and status != "Success":
        # Update the attempts counter by 1
        # and then proceed as normal
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"attempts": attempts+1}
        ) 
        return_status = normal_processing(received_msg, mongo_db)
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": return_status}
        )
    elif attempts >= 10 and status != "Failed":
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": "Failed"}
        )
    # Send an acknowledgement to for current message
    channel.basic_ack(delivery_tag=method.delivery_tag)

def pulsar_callback_func(received_msg):
    global mongo_db, repo_download_path

    # Log the fetched repositories name and link
    # along with other attributes to database
    received_msg = json.loads(received_msg)

    # Fetch number of existing attempts
    # on the current repository
    attempts, status = mongo_db.fetch_attempts_and_status(reponame=received_msg["reponame"], repolink=received_msg["html_url"])

    if attempts == 0:
        # The record does not exist, create an entry
        # for current repo and then proceed as normal
        mongo_db.insert_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            topics=received_msg["topics"],
            visibility=received_msg["visibility"],
            stargazers_count=received_msg["stargazers_count"],
            language=received_msg["language"],
            status="Processing"
        )
        return_status = normal_processing(received_msg, mongo_db)
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": return_status}
        )
    elif attempts < 10:
        # Update the attempts counter by 1
        # and then proceed as normal
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"attempts": attempts+1}
        ) 
        return_status = normal_processing(received_msg, mongo_db)
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": return_status}
        )
    elif attempts >= 10 and status != "Failed":
        # Update the status to failed
        mongo_db.update_gitrepo(
            reponame=received_msg["reponame"],
            repolink=received_msg["html_url"],
            updates={"status": "Failed"}
        )

    return True

if __name__=="__main__":
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
    parser.add_argument(
        "--download-path",
        type=str,
        required=False,
        default="/testRepo",
    )
    args = parser.parse_args()
    
    # Consumer messages
    global mongo_db, repo_download_path
    repo_download_path = args.download_path
    mongo_db = CustomMongoDB()
    
    if args.pulsar:
        from pulsar_consumer import Consumer
        cons = Consumer(host="pulsar", port=6650, topic=args.target_queue)
        cons.consume(callback=pulsar_callback_func)
    else:        
        from rabbit_consumer import Consumer
        cons = Consumer(host="rabbit", port=5672, username="rabbitmq", password="rabbitmq", queue=args.target_queue)
        cons.consume(callback=rabbit_callback_func)

