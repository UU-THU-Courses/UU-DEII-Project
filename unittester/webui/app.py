import os, io
import argparse
from helpers import MongodbReader, generate_summary

from flask import (
    Flask,
    request,
    send_file,
    render_template,
    after_this_request
)

app = Flask(__name__)
mongo_reader = MongodbReader()

@app.route("/")
def dashboard():
    return render_template("index.html", message="This is a success message", message_type="SUCCESS")

@app.route("/summary")
def queue_summary():
    summary = generate_summary(mongo_reader=mongo_reader)
    return render_template(
        "summary.html", 
        summary=summary,
        refresh=True,
    )

@app.route("/git-repos")
def git_repors():
    repo_info = mongo_reader.fetch_repositories()
    if len(repo_info) > 0:
        message = f"Found a total of {len(repo_info)} repositories logged in the database."
        message_type = "SUCCESS"  
    else:
        message = f"No repository found in the database."
        message_type = "WARNING"
    
    return render_template(
        template_name_or_list="repos.html", 
        message=message,
        message_type=message_type,
        repo_info=repo_info,
        refresh=True,
    )

@app.route("/unittests")
def unit_tests():
    repo_info = mongo_reader.fetch_summary()
    if len(repo_info) > 0:
        message = f"Found a total of {len(repo_info)} repositories logged in the database."
        message_type = "SUCCESS"  
    else:
        message = f"No repository found in the database."
        message_type = "WARNING"

    return render_template(
        template_name_or_list="unittests.html", 
        message=message,
        message_type=message_type,
        repo_info=repo_info,
        refresh=True,
    )

@app.route("/failures")
def failures():
    repo_info = mongo_reader.fetch_failures()
    if len(repo_info) > 0:
        message = f"Found a total of {len(repo_info)} repositories logged in the database."
        message_type = "SUCCESS"  
    else:
        message = f"No repository found in the database."
        message_type = "WARNING"

    return render_template(
        template_name_or_list="failures.html", 
        message=message,
        message_type=message_type,
        repo_info=repo_info,
        refresh=True,
    )

@app.route("/cluster")
def cluster_status():
    return render_template("cluster.html")

@app.route("/download-report/<record_id>")
def download_report(record_id):
    # Fetch the exception for the requested record
    full_record = mongo_reader.fetch_exception(record_id)
    # Build file path
    file_name = f"{full_record['reponame']}.txt"
    file_path = f"/{file_name}"
    # Write the exception to a file for download
    with open(file_path, "w") as outfile:
        outfile.write(f"Repository  : {full_record['reponame']}\n")
        outfile.write(f"Repo Link   : {full_record['repolink']}\n\n\n")
        outfile.write(f"Console Log : \n")
        outfile.write(f"------------- \n\n")
        outfile.write(f"{full_record['exception']}\n")
    # Read the file into a io object for
    # later transmission, this method makes
    # it possible for us to remove the file
    # before sending its content. 
    return_data = io.BytesIO()
    with open(file_path, "rb") as outfile:
        return_data.write(outfile.read())
    return_data.seek(0)
    # Remove the file from local disk
    os.remove(file_path)
    # Return the file as an attachment.
    return send_file(return_data, mimetype="text/plain", download_name=file_name, as_attachment=True)
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--host",
        required=False,
        default="0.0.0.0",
        type=str,
    )
    parser.add_argument(
        "--port",
        required=False,
        default=5100,
        type=int,
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    app.run(host = args.host,port=args.port,debug=args.debug)
    del mongo_reader
    del app
