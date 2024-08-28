from cs50 import SQL
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from functools import wraps
import hashlib

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///project.db")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function

def render_error(m):
    return render_template("error.html", message=m)

# got this function from here: https://www.tutorialspoint.com/how-to-hash-passwords-in-python
def hash_password(password): 
    password_bytes = password.encode('utf-8')
    hash_object = hashlib.sha256(password_bytes)
    return hash_object.hexdigest()

dists = []
def load_dists():
    rows = db.execute("SELECT distance FROM distances WHERE user_id = ?", session["user_id"])
    for row in rows:
        if row["distance"] not in dists:
            dists.append(row["distance"])

@app.route("/")
@login_required
def index():
    load_dists()
    return render_template("index.html", dists=dists)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear();

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return render_error("Missing Credentials!")
        
        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(user) != 1 or (hash_password(password) != user[0]["pass_hash"]):
            return render_error("Invalid username or password!")
        
        session["user_id"] = user[0]["id"]

        return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("password_conf")

        if not username or not password or not confirmation:
            return render_error("Missing credentials!")
        
        if password != confirmation:
            return render_error("Passwords do not match!")
        
        password_hash = hash_password(password)

        try:
            db.execute("INSERT INTO users (username, pass_hash) VALUES (?, ?)", username, password_hash)
        except ValueError:
            return render_error("User is already registered!")
        
        return redirect("/")
        

@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

@app.route("/adddist")
@login_required
def adddist():
    distance = request.args["distance"]

    if not distance:
        return render_error("Missing distance!")
    
    if not db.execute("SELECT * FROM distances WHERE user_id = ? AND distance = ?", session["user_id"], distance):
        db.execute("INSERT INTO distances (user_id, distance) VALUES (?, ?)", session["user_id"], distance)
        return redirect("/")
    else:
        return render_error("Distance already exists!")

if __name__ == "__main__":
    app.run(debug=True)

