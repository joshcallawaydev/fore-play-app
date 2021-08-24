import os
from flask import (
    Flask, render_template, url_for,
    flash, redirect, request, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if user already exists
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("User already exists")
            return redirect(url_for("login"))

        # add new user
        new_user = {
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "handicap": request.form.get("handicap"),
            "home_course": request.form.get("home_course"),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name")
        }
        mongo.db.users.insert_one(new_user)

        # put user in session cookie with mongo id
        session["user"] = str(new_user["_id"])
        flash("Registration Successful")
        return redirect(url_for("profile", id=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if email in db
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = str(existing_user["_id"])
                flash("Welcome, {}".format(existing_user["first_name"]))
                return redirect(url_for("profile", id=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<id>", methods=["GET", "POST"])
def profile(id):
    # grab the id from db
    user = mongo.db.users.find_one(
        {"_id": ObjectId(id)})

    if session["user"]:
        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


@app.route("/edit_profile/<id>", methods=["GET", "POST"]) 
def edit_profile(id):
    # grab user from database
    user = mongo.db.users.find_one(
        {"_id": ObjectId(id)})

    if request.method == "POST":
        # edit user details
        edit = {
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "handicap": request.form.get("handicap"),
            "home_course": request.form.get("home_course"),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name")
        }
        mongo.db.users.update({"_id": ObjectId(id)}, edit)
        flash("Profile updated!")
        return render_template("profile.html", user=user)

    return render_template("edit_profile.html", user=user)


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
