import os
import shutil
import argparse
import subprocess

from consolidate import process_reports
from database import CustomMongoDB

def rabbit_callback_func(channel, method, properties, body):
    global mongo_db, repo_download_path
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    received_msg = body.decode()
    run_command = rf"bash runtest.sh {received_msg} /testRepo"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports(xmlpath=f"{repo_download_path}/target/surefire-reports")
    # Insert results to database only
    # it there is at least 1 test
    # that was run (fail / pass)
    if results_dict["tests"] > 0 or results_dict["exception"] != "":
        mongo_db.insert_summary(
            reponame=os.path.splitext(os.path.basename(received_msg))[0],
            repolink=received_msg,
            tests=results_dict["tests"],
            errors=results_dict["errors"],
            skipped=results_dict["skipped"],
            failures=results_dict["failures"],
            runtime=results_dict["runtime"],
            exception=results_dict["exception"]
        )
    else:
        console_file = f"{repo_download_path}/temp-console-output-file.txt"
        if os.path.isfile(console_file):
            with open(console_file, "r") as f:
                console_log = f.read()
        else:
            console_log = "No console file exists... Some error downloading git repository?"
        
        # Insert error to the errors table
        mongo_db.insert_errors(
            reponame=os.path.splitext(os.path.basename(received_msg))[0],
            repolink=received_msg,
            exception=console_log
        )
    # Perform clean up of temporary paths
    shutil.rmtree(repo_download_path)
    # Send an acknowledgement to for current message
    channel.basic_ack(delivery_tag=method.delivery_tag)

def pulsar_callback_func(received_msg):
    global mongo_db, repo_download_path
    # Build the command to call the script that
    # downloads git repo and runs maven tests
    run_command = rf"bash runtest.sh {received_msg} {repo_download_path}"
    subprocess.call(run_command, shell=True)
    # Process the results using the process
    # reports module in consolidate.py
    results_dict = process_reports(xmlpath=f"{repo_download_path}/target/surefire-reports")
    # Insert results to database only
    # it there is at least 1 test
    # that was run (fail / pass)
    if results_dict["tests"] > 0 or results_dict["exception"] != "":
        mongo_db.insert_summary(
            reponame=os.path.splitext(os.path.basename(received_msg))[0],
            repolink=received_msg,
            tests=results_dict["tests"],
            errors=results_dict["errors"],
            skipped=results_dict["skipped"],
            failures=results_dict["failures"],
            runtime=results_dict["runtime"],
            exception=results_dict["exception"]
        )
    else:
        with open(f"{repo_download_path}/temp-console-output-file.txt", "r") as f:
            console_log = f.read()
        mongo_db.insert_errors(
            reponame=os.path.splitext(os.path.basename(received_msg))[0],
            repolink=received_msg,
            exception=console_log
        )  
    # Perform clean up of temporary paths
    shutil.rmtree(repo_download_path)
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

