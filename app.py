from cs50 import SQL
import datetime
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
    dists.clear()
    rows = db.execute("SELECT distance FROM distances WHERE user_id = ?", session["user_id"])
    for row in rows:
        if row["distance"] not in dists:
            dists.append(row["distance"])

def dist_to_id(distance):
    return db.execute("SELECT id FROM distances WHERE distance = ? AND user_id = ?", distance, session["user_id"])[0]["id"]

def id_to_dist(id):
    return db.execute("SELECT distance FROM distances WHERE id = ?", id)[0]["distance"]

def get_pr(distance):
    r = db.execute("SELECT * FROM times WHERE dist_id = ? ORDER BY h ASC, m ASC, s ASC, ms ASC, date DESC", dist_to_id(distance))
    if len(r) == 0:
        return {}
    return r[0]

@app.route("/")
@login_required
def index():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

    times = db.execute("SELECT * FROM times WHERE user_id = ? ORDER BY date DESC", session["user_id"])
    for time in times:
        time["distance"] = db.execute("SELECT distance FROM distances WHERE id = ?", time["dist_id"])[0]["distance"]

    distances = db.execute("SELECT * FROM distances WHERE user_id = ?", session["user_id"])
    prs=[]
    for d in distances:
        if get_pr(d["distance"]) != {}:
            prs.append(get_pr(d["distance"]))
    
    for pr in prs:
        pr["distance"] = db.execute("SELECT distance FROM distances WHERE id = ?", pr["dist_id"])[0]["distance"]
    
    load_dists()
    return render_template("index.html", dists=dists, username=username, times=times, prs=prs)

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

@app.route("/log", methods=["GET", "POST"])
@login_required
def log():
    times = db.execute("SELECT * FROM times WHERE times.user_id = ? ORDER BY date DESC", session["user_id"])
    for time in times:
        time["distance"] = db.execute("SELECT distance FROM distances WHERE id = ?", time["dist_id"])[0]["distance"]
    load_dists()
    return render_template("log.html", dists=dists, times=times)

@app.route("/addentry", methods=["GET", "POST"])
@login_required
def addentry():
    if request.method == "GET":
        load_dists()
        return render_template("addentry.html", dists=dists)
    else:
        distance = request.form.get("distance")
        h = request.form.get("h")
        m = request.form.get("m")
        s = request.form.get("s")
        ms = request.form.get("ms")
        date = request.form.get("date")
        notes = request.form.get("notes")

        if not distance:
            return render_error("Missing distance!")
        
        if not h:
            h = 0
        else:
            h = int(h)
        
        if not m:
            m = 0
        else:
            m = int(m)

        if not s:
            s = 0
        else:
            s = int(s)

        if not ms:
            ms = 0
        else:
            ms = int(ms)

        if not date:
            return render_error("Missing date!")
        
        if (h < 0) or (m < 0) or (m > 59) or (s < 0) or (s > 59) or (ms < 0) or (ms > 999):
            return render_error("Invalid time!")
        
        dist_id = db.execute("SELECT id FROM distances WHERE user_id = ? AND distance = ?", session["user_id"], distance)[0]["id"]
        if not dist_id:
            return render_error("Distance does not exist!")

        db.execute("INSERT INTO times (user_id, dist_id, h, m, s, ms, date, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", session["user_id"], dist_id, h, m, s, ms, date, notes)
        
        return redirect("/log")

@app.route("/deleteentry", methods=["GET", "POST"])
@login_required
def deleteentry():
    if request.method == "GET":
        entry = db.execute("SELECT * FROM times WHERE id = ?", request.args.get("id"))[0]
        entry["distance"] = db.execute("SELECT distance FROM distances WHERE user_id = ? AND id = ?", session["user_id"], entry["dist_id"])[0]["distance"]
        load_dists()
        return render_template("deleteentry.html", dists=dists, entry=entry)
    else:
        if hash_password(request.form.get("password")) == db.execute("SELECT pass_hash FROM users WHERE id = ?", session["user_id"])[0]["pass_hash"]:
            db.execute("DELETE FROM times WHERE id = ?", request.form.get("id"))
            return redirect("/log")
        else:
            return render_error("Wrong Password!")

@app.route("/distance/<dist>")
@login_required
def distance(dist):
    times = db.execute("SELECT times.id, times.user_id, h, m, s, ms, date, notes, dist_id FROM times JOIN distances ON times.dist_id = distances.id WHERE times.user_id = ? AND distance = ? ORDER BY date DESC", session["user_id"], dist)
    xArray = []
    yArray = []
    for time in times:
        time["distance"] = db.execute("SELECT distance FROM distances WHERE id = ?", time["dist_id"])[0]["distance"]
        xArray.append(time["date"])
        yArray.append(time["h"] * 3600 + time["m"] * 60 + time["s"] + time["ms"] / 1000) 

    pr = get_pr(dist)   

    load_dists()
    return render_template("distance.html", dists=dists, dist=dist, times=times, xArr=xArray, yArr=yArray, pr=pr)


@app.route("/distance/<dist>/editname", methods=["GET", "POST"])
@login_required
def editname(dist):
    if request.method == "GET":
        load_dists()
        return render_template("editname.html", dist=dist, dists=dists)
    else:
        if hash_password(request.form.get("password")) == db.execute("SELECT pass_hash FROM users WHERE id = ?", session["user_id"])[0]["pass_hash"]:
            name = request.form.get("name")
            if name in dists:
                return render_error("Distance already exists!")
            
            db.execute("UPDATE distances SET distance = ? WHERE distance = ? AND user_id = ?", name, dist, session["user_id"])
            if dist in dists:
                dists.remove(dist)
            return redirect("/distance/" + name)
        else:
            return render_error("Wrong Password!")
    

@app.route("/distance/<dist>/deletedistance", methods=["GET", "POST"])
@login_required
def deletedistance(dist):
    if request.method == "GET":
        load_dists()
        return render_template("deletedistance.html", dist=dist, dists=dists)
    else:
        if hash_password(request.form.get("password")) == db.execute("SELECT pass_hash FROM users WHERE id = ?", session["user_id"])[0]["pass_hash"]:
            db.execute("DELETE FROM times WHERE dist_id = ? AND user_id = ?", dist_to_id(dist), session["user_id"])
            db.execute("DELETE FROM goals WHERE dist_id = ? AND user_id = ?", dist_to_id(dist), session["user_id"])
            db.execute("DELETE FROM distances WHERE distance = ? AND user_id = ?", dist, session["user_id"])
            if dist in dists:
                dists.remove(dist)
            return redirect("/")
        else:
            return render_error("Wrong Password!")

@app.route("/goals")
@login_required
def goals():
    if db.execute("SELECT * FROM times WHERE user_id = ?", session["user_id"]) == []:
        return render_error("Please add times first!")
    goals = db.execute("SELECT * FROM goals WHERE user_id = ? ORDER BY status ASC, id DESC", session["user_id"])
    for goal in goals:
        goal["distance"] = id_to_dist(goal["dist_id"])
        pr = get_pr(goal["distance"])
        goal["pr_time"] = "%02d:%02d:%02d.%03d" % (pr["h"], pr["m"], pr["s"], pr["ms"])

        if goal["status"] == 0:
            goaltime = goal["h"] * 3600 + goal["m"] * 60 + goal["s"] + goal["ms"] / 1000
            prtime = pr["h"] * 3600 + pr["m"] * 60 + pr["s"] + pr["ms"] / 1000

            if prtime <= goaltime:
                db.execute("UPDATE goals SET status = 1, completion_date = ? WHERE id = ?", pr["date"], goal["id"])
                goal["completion_date"] = pr["date"]
                goal["status_text"] = "Completed on " + goal["completion_date"]
                goal["class"] = "tr_complete"
            else:
                goal["status_text"] = "In Progress: "
                due = datetime.datetime.strptime(goal["due_date"], "%Y-%m-%d")
                tod = datetime.datetime.today()
                remdays = due - tod
                if remdays.days >= -1:
                    goal["status_text"] += str(remdays.days + 1) + " " + ("day" if remdays.days + 1 == 1 else "days") + " remaining"
                    goal["class"] = "tr_progress"
                else:
                    goal["status_text"] += str(abs(remdays.days + 1)) + " " + ("day" if abs(remdays.days + 1) == 1 else "days") + " overdue"
                    goal["class"] = "tr_overdue"
        else:
            goal["status_text"] = "Completed on " + goal["completion_date"]
            goal["class"] = "tr_complete"

    load_dists()
    return render_template("goals.html", dists=dists, goals=goals)

@app.route("/addgoal", methods=["GET", "POST"])
@login_required
def addgoal():
    if request.method == "GET":
        load_dists()
        return render_template("addgoal.html", dists=dists)
    else:
        distance = request.form.get("distance")
        h = request.form.get("h")
        m = request.form.get("m")
        s = request.form.get("s")
        ms = request.form.get("ms")
        date = request.form.get("date")
        notes = request.form.get("notes")

        if not distance:
            return render_error("Missing distance!")
        
        if not h:
            h = 0
        else:
            h = int(h)
        
        if not m:
            m = 0
        else:
            m = int(m)

        if not s:
            s = 0
        else:
            s = int(s)

        if not ms:
            ms = 0
        else:
            ms = int(ms)

        if not date:
            return render_error("Missing date!")
        
        if (datetime.datetime.strptime(date, "%Y-%m-%d") < datetime.datetime.today()):
            return render_error("Invalid date!")
        
        if (h < 0) or (m < 0) or (m > 59) or (s < 0) or (s > 59) or (ms < 0) or (ms > 999):
            return render_error("Invalid time!")
        
        dist_id = db.execute("SELECT id FROM distances WHERE user_id = ? AND distance = ?", session["user_id"], distance)[0]["id"]
        if not dist_id:
            return render_error("Distance does not exist!")

        db.execute("INSERT INTO goals (user_id, dist_id, h, m, s, ms, due_date, notes, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)", session["user_id"], dist_id, h, m, s, ms, date, notes)
        
        return redirect("/goals")

@app.route("/deletegoal", methods=["GET", "POST"])
@login_required
def deletegoal():
    if request.method == "GET":
        goal = db.execute("SELECT * FROM goals WHERE id = ?", request.args.get("id"))[0]
        goal["distance"] = db.execute("SELECT distance FROM distances WHERE user_id = ? AND id = ?", session["user_id"], goal["dist_id"])[0]["distance"]
        load_dists()
        return render_template("deletegoal.html", dists=dists, goal=goal)
    else:
        if hash_password(request.form.get("password")) == db.execute("SELECT pass_hash FROM users WHERE id = ?", session["user_id"])[0]["pass_hash"]:
            db.execute("DELETE FROM goals WHERE id = ?", request.form.get("id"))
            return redirect("/goals")
        else:
            return render_error("Wrong Password!")

if __name__ == "__main__":
    app.run()

