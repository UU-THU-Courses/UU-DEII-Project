import argparse
from flask import (
   Flask,
   request,
   jsonify,
   Markup,
   render_template 
)

#app = Flask(__name__, template_folder='./templates',static_folder='./static')
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("tabs.html")

@app.route("/accuracy", methods=['POST', 'GET'])
def accuracy():
    # if request.method == 'POST':
    #     r = get_accuracy.delay()
    #     a = r.get()
    #     return '<h1>The accuracy is {}</h1>'.format(a)

    return '''<form method="POST">
    <input type="submit">
    </form>'''

@app.route("/predictions", methods=['POST', 'GET'])
def predictions():
    # if request.method == 'POST':
    #     results = get_predictions.delay()
    #     predictions = results.get()

    #     results = get_accuracy.delay()
    #     accuracy = results.get()
        
    #     final_results = predictions

    #     return render_template('result.html', accuracy=accuracy ,final_results=final_results) 
                    
    return '''<form method="POST">
    <input type="submit">
    </form>'''

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
        default=False,
    )
    args = parser.parse_args()

    app.run(host = args.host,port=args.port,debug=args.debug)
