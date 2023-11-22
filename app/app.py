from flask import Flask, render_template, abort, request, url_for, redirect
from pymongo import MongoClient
import glob
import re
import json
import hashlib

# iniialise Flask application
app = Flask(__name__)

# create a connection to mongodb
client = MongoClient('db', 27017, username='root', password='root')

# use the "data_fabric" database
db = client.data_fabric

@app.route('/')
def models():
    # get list of all json files in models folder
    files = glob.glob('models/*.json')

    # filter out any json files that do not represent valid model files (xxx-ModelName.json)
    matches = [re.search(r'(\d{3})\-(\w+)\.json',file) for file in files]

    # create list of models ready for template rendering
    models = [{"id":model[1], "name":model[2]} for model in matches]

    return render_template('models.html', title="Models", models=models)

@app.route('/model/<id>', methods=('GET', 'POST'))
def model(id):
    # check if request is for a valid model, throw 404 if not
    files = glob.glob(f"models/{id:0>3}-*.json")
    if not files:
        abort(404)
    
    # extract id and model name from filename
    matches = re.search(r'(\d{3})\-(\w+)\.json',files[0])
    
    # check if form has been submitted
    if request.method == 'POST':
        # generate json string from form contents
        scen = json.dumps(request.form)

        # generate md5 hash of scenario json for uniqueness check
        cs = hashlib.md5(scen.encode("utf-8")).hexdigest()

        # use a collection named after the model (equivalent to a table in SQL)
        model = matches[0][0:-5] # remove .json extension from model filename
        collection = db[model]
        
        # query mongo database to see if this run has been previously performed using the model name and scenario hash
        check = collection.find_one({'hash':cs})

        # if nothing is found, this is a new run so insert in to the database
        to_print = [scen, cs]
        if not check:
            meta = {'hash':cs, 'scenario':request.form}
            collection.insert_one(meta)
            to_print = ['New Run'] + to_print
        else:
            to_print = ['Existing Run'] + to_print
        
        return render_template('debug.html', to_print=to_print)
    
    # for not submitted (GET request), so read model schema
    with open(files[0]) as f:
        form_json = f.read()
    
    # display scenario entry form to user
    return render_template('model.html', model=matches[2], form_json=form_json)