from flask import Flask, render_template, request, session, redirect
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

dists = ["100m", "400m", "5K", "10K"]

@app.route("/")
def index():
    return render_template("index.html", dists=dists)