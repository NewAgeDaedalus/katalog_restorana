from flask import Flask, url_for, redirect, session, render_template, send_file
from urllib.parse import quote_plus, urlencode
from os.path import join
from flask import request
from zipfile import ZipFile
import subprocess
from io import BytesIO
import json

from data_manager import Restoran_fetcher, Restoran_manager, ChangeException

from authlib.integrations.flask_client import OAuth


app = Flask(__name__)

html_template_dir = "./templates"
scripts_dir = "./frontend"

app.secret_key = "0590c30bf2c685d95787f03ef7f7d8b4a5b06157f8b0b8738692bcaaf57141df"  # Replace with your own secure key

AUTH0_CLIENT_ID = "7UueyWtG4n46pFY1B6PxCcncuTkV391Q"
AUTH0_CLIENT_SECRET = "qO1ut-vQfyg2_PNEKo8EUD_Mu_I1wwqoVDHPTSG-tMW7ZTMdjEloN_4ocVVKZaFf"
AUTH0_DOMAIN = "dev-h6zmryj30mydxbir.us.auth0.com"

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{AUTH0_DOMAIN}/.well-known/openid-configuration'
)

@app.route('/login')
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route('/callback', methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + AUTH0_DOMAIN
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("index", _external=True),
                "client_id": AUTH0_CLIENT_ID
            },
            quote_via=quote_plus,
        )
    )

@app.route("/user")
def user():
    return render_template("user.html", session=session["user"])

@app.route("/")
def index():
    with open(join(html_template_dir, "index.html"), "r") as file:
        return file.read()

@app.route("/preuzmi")
def preuzmi():
    subprocess.run(["bash", "./export_csv.sh",  "restorani.csv"])
    subprocess.run(["python", "export_to_json.py", "fabian", "restorani.json"])
    stream = BytesIO()
    with ZipFile(stream, 'w') as zf:
        zf.write("restorani.csv", "restorani.csv")
        zf.write("restorani.json", "restorani.json")
    stream.seek(0)

    return send_file(
        stream,
        as_attachment=True,
        download_name='katalog_restorana.zip'
    )


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
    try:
        restorani_to_update = json.loads(request.get_data())
    except:
        return {
            "status": "ERROR",
            "message": "JSON badly formed"
        }, 400
    restorani_manager = Restoran_manager()
    indx, msg = restorani_manager.update_restorani(restorani_to_update)
    if indx != None:
        return {
                "status": "ERROR",
                "message": f"Malformed entry at index {indx}. " + msg
        }, 400
    return {
            "status": "OK",
            "message": "Restorani updated successfully"
    }, 200

@app.route('/rest/api/restoran/<oib_restoran>', methods = ['DELETE'])
def delete_restoran(oib_restoran):
    restoran_manager = Restoran_manager()
    try:
        restoran_manager.delete_restoran(oib_restoran)
    except ChangeException as e:
        return {
            "status": "ERROR",
            "message": e
        }, 400
    return {
            "status": "OK",
            "message": f"successfully deleted object with id {oib_restoran}"
    }, 200

