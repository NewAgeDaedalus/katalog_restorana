from flask import Flask
from os.path import join
from flask import request
import json

from data_manager import Restoran_fetcher, Restoran_manager

app = Flask(__name__)

html_template_dir = "./templates"
scripts_dir = "./frontend"

@app.route("/")
def index():
    with open(join(html_template_dir, "index.html"), "r") as file:
        return file.read()

@app.route("/katalog")
def show_data():
    with open(join(html_template_dir, "data.html"), "r") as file:
        return file.read()

@app.route("/main.js")
def serve_frontend():
    with open(join(scripts_dir, "main.js"), "r") as file:
        return file.read()


@app.route("/data/api/<args>")
def get_data(args):
    print(args)
    fetcher = Restoran_fetcher()
    if args == "All":
        return fetcher.fetch()
    else:
        return fetcher.fetch(args=json.loads(args))

@app.route("/rest/api/restorani/all")
def get_all_restorani():
    fetcher = Restoran_fetcher()
    #try:
    try:
        restorani = fetcher.fetch()
    except:
        return {
            "status": "ERROR",
            "message": "Internal server error"
        }, 500
    return {
            "status": "OK",
            "message": "Fetched all restorani objects",
            "response": restorani
    }, 200

@app.route("/rest/api/restorani/oib/<id>")
def get_restoran(id):
    fetcher = Restoran_fetcher()
    try:
        restoran = fetcher.fetch({"oib":id}, fuzzy=False)
    except:
        return {
            "status": "ERROR",
            "message": "Internal server error"
        }, 500
    return {
            "status": "OK",
            "message": "Fetched specific restoran",
            "response": restoran
    }, 200

@app.route("/rest/api/restorani/name/<name>")
def get_restoran_by_name(name):
    fetcher = Restoran_fetcher()
    try:
        restoran = fetcher.fetch({"ime":name}, fuzzy=False)
    except:
        return {
            "status": "ERROR",
            "message": "Internal server error"
        }, 500
    return {
            "status": "OK",
            "message": "Fetched specific restoran",
            "response": restoran
    }, 200

@app.route("/rest/api/restorani/open")
def get_open_restoran():
    fetcher = Restoran_fetcher()
    try:
        restorani = fetcher.fetch({"datum_zatvaranja":"None"}, fuzzy=False)
    except:
        return {
            "status": "ERROR",
            "message": "Internal server error"
        }, 500
    return {
            "status": "OK",
            "message": "Fetched specific restoran",
            "response": restorani
    }, 200

@app.route("/rest/api/restorani/michelin/<zvijezda>")
def get_michelin_restoran(zvijezda):
    fetcher = Restoran_fetcher()
    try:
        restorani = fetcher.fetch({"michelin_zvjezdica":zvijezda}, fuzzy=False)
    except:
         return {
             "status": "ERROR",
             "message": "Internal server error"
         }, 500
    return {
            "status": "OK",
            "message": "Fetched specific restoran",
            "response": restorani
    }, 200

@app.route('/rest/api/restoran', methods = ['POST'])
def create_restorani():
    new_restorani = json.loads(request.get_data())
    restorani_manager = Restoran_manager()
    failed= restorani_manager.create_restorani(new_restorani)
    if failed  == []:
        return {
            "status": "OK",
            "message": f"Created {len(new_restorani)} restorantes",
        }, 200
    elif len(failed) == len(new_restorani):
        return {
            "status": "ERROR",
            "message": f"Bad request, restorantes badly formated"
        },400 
    else:
        return {
            "status": "ERROR",
            "message": f"Partially correct, created {len(new_restorani)-len(failed)} restorantes"
        },400 
    return "OK"

@app.route('/rest/api/restoran', methods = ['PUT'])
def update_restorani():
    print("?")
    restorani_to_update = json.loads(request.get_data())
    print(restorani_to_update)
    restorani_manager = Restoran_manager()
    restorani_manager.update_restorani(restorani_to_update)


@app.route('/rest/api/restoran/<id>', methods = ['DELETE'])
def delete_restorani(oib_restoran):
    restorani_manager = Restoran_manager()
    Restoran_manager.delete(oib_restoran)
