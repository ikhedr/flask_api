
from flask import Flask, make_response, request, render_template, jsonify
import io
import csv
from flask_pymongo import PyMongo
import pandas as pd
import json
from bson import ObjectId

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


app = Flask(__name__,template_folder='templates')

#Database name
app.config['MONGO_DBNAME'] = 'tickets'

# use mlab.com to take temperory dbs
#mongodb://<dbuser>:<dbpassword>@ds241012.mlab.com:41012/DatabaseName

app.config['MONGO_URI'] = 'mongodb://datta:datta1@ds241012.mlab.com:41012/tickets'

mongo = PyMongo(app)


def transform(text_file_contents):
    return text_file_contents.replace("=", ",")


@app.route('/')
def form():
    return """
        <html>
            <body>
                <h2>Upload ticket data to be predicted(csv format)</h2>

                <form action="/insert" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" />
                </form>
            </body>
        </html>
    """

@app.route('/insert', methods=["POST"])
def db_insert_from_csv():
    users = mongo.db.users
    #csv file of users
    f = request.files['data_file']
    if not f:
        return "No file"

    stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)

    stream.seek(0)
    result = transform(stream.read())

    #create list of dictionaries keyed by header row
    csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(result.splitlines(), \
        skipinitialspace=True)]

    result1 = users.insert_many(csv_dicts)
    return "Records inserted into DB"

@app.route('/display')
def display():
    users = mongo.db.users
    lst = {}
    for post in users.find():
        lst.update(post)
    lst = JSONEncoder().encode(lst)
    return jsonify(lst)
    #return render_template('users.html',usr_list = lst)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)