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
    """
    Registration page function
    Checks for user,
    if nothing active,
    adds new user to db,
    then adds to session cookie
    """
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
    """
    Login page function
    again checks for user,
    if available, checks password,
    then directs to profile
    """
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
    """
    Profile page function
    pulls profile detail from db
    """
    # grab the id from db
    user = mongo.db.users.find_one(
        {"_id": ObjectId(id)})

    if session["user"]:
        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


@app.route("/edit_profile/<id>", methods=["GET", "POST"])
def edit_profile(id):
    """
    Edit profile function
    find user in db,
    redirects to edit_profile.html,
    allows entry to be updated
    """
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


@app.route("/tracker/<id>")
def tracker(id):
    """
    Course tracker and review function
    """

    courses = list(mongo.db.courses.find({"user_id": id}))

    return render_template(
        "tracker.html", user_id=session["user"], courses=courses)


@app.route("/add_course/<id>", methods=["GET", "POST"])
def add_course(id):
    """
    Function to add a new course
    to your tracker
    """

    user = mongo.db.users.find_one(
        {"_id": ObjectId(id)})

    if request.method == "POST":

        new = {
            "course_name": request.form.get("course_name").lower(),
            "course_length": request.form.get("course_length"),
            "course_par": request.form.get("course_par"),
            "course_holes": request.form.get("course_holes"),
            "course_your_score": request.form.get("course_your_score"),
            "course_date": request.form.get("course_date"),
            "course_comments": request.form.get("course_comments").lower(),
            "course_your_name": request.form.get("course_your_name").lower(),
            "course_image": request.form.get("course_image"),
            "user_id": id
        }
        mongo.db.courses.insert_one(new)
        flash("Course Added!")

        return redirect(url_for("tracker", new=new, id=session["user"]))

    return render_template("add_course.html", user=user)


@app.route("/edit_tracker/<cid>", methods=["GET", "POST"])
def edit_tracker(cid):
    """
    function for editting a course in your tracker
    """
    course = mongo.db.courses.find_one({"_id": ObjectId(cid)})

    if request.method == "POST":

        edit = {
            "course_name": request.form.get("course_name").lower(),
            "course_length": request.form.get("course_length"),
            "course_par": request.form.get("course_par"),
            "course_holes": request.form.get("course_holes"),
            "course_your_score": request.form.get("course_your_score"),
            "course_date": request.form.get("course_date"),
            "course_comments": request.form.get("course_comments").lower(),
            "course_your_name": request.form.get("course_your_name").lower(),
            "course_image": request.form.get("course_image"),
            "user_id": id
        }
        mongo.db.courses.update({"_id": ObjectId(cid)}, edit)
        flash("Course successfully updated")

        return redirect(url_for("tracker.html", user=session["user"]))

    return render_template(
        "edit_tracker.html", course=course, user=session["user"])


@app.route("/delete_course/<id>", methods=["GET"])
def delete_course(id):
    """
    Function for deleting courses from your tracker
    """

    mongo.db.courses.delete_one({"_id": ObjectId(id)})

    return redirect(url_for("tracker", id=session["user"]))


@app.route("/logout")
def logout():
    """
    Logout function
    removes user from session cookie
    """
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(e):
    """
    A customer error 404 page
    page has redirects to home and profile
    """
    return render_template("404.html", e=e)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
