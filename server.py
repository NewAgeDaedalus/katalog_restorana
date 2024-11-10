from flask import Flask
from os.path import join
from flask import request
import json

from data_manager import Restoran_fetcher

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
