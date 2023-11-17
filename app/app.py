from flask import Flask, render_template, abort, request
import glob
import re
import json
import hashlib

app = Flask(__name__)

@app.route('/')
def models():
    files = glob.glob('models/*.json')
    matches = [re.search(r'(\d{3})\-(\w+)\.json',file) for file in files]
    models = [{"id":model[1], "name":model[2]} for model in matches]
    return render_template('models.html', title="Models", models=models)

@app.route('/model/<id>', methods=('GET', 'POST'))
def model(id):
    if request.method == 'POST':
        scen = json.dumps(request.form)
        cs = hashlib.md5(y.encode("utf-8")).hexdigest()
        to_print = [scen,cs]
        return render_template('debug.html', to_print=to_print)
    files = glob.glob(f"models/{id:0>3}-*.json")
    if not files:
        abort(404)
    matches = re.search(r'(\d{3})\-(\w+)\.json',files[0])
    with open(files[0]) as f:
        form_json = f.read()
    return render_template('model.html', model=matches[2], form_json=form_json)