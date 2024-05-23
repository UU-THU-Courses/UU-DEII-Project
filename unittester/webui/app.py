# from asyncio import sleep
import argparse
from helpers import MongodbReader
from flask import (
   Flask,
#    request,
#    jsonify,
#    Markup,
#    Response,
#    make_response,
   render_template 
)
# from flask_socketio import SocketIO

app = Flask(__name__)
mongo_reader = MongodbReader()

@app.route('/')
def dashboard():
    return render_template("index.html", message="This is a success message", message_type="SUCCESS")

@app.route('/queues')
def queue_status():
    return render_template("queues.html", message="This is a warning message", message_type="WARNING")

@app.route('/git-repos')
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
        repo_info=repo_info
    )

@app.route('/unittests')
def unit_tests():
    return render_template("unittests.html")

@app.route('/failures')
def failures():
    return render_template("failures.html")

@app.route('/cluster')
def cluster_status():
    return render_template("cluster.html")

if __name__ == '__main__':
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
        default=True,
    )
    args = parser.parse_args()

    app.run(host = args.host,port=args.port,debug=args.debug)
