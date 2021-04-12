import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SEKRET_KEY")

mongo = PyMongo(app)

API_KEY = os.environ.get('API_KEY')
SEARCH_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q='
VOLUME_BASE_URL = 'https://www.googleapis.com/books/v1/volumes/'

@app.route("/")
def home():
    return render_template('index.html')


@app.route("/profile/", methods=["GET", "POST"])
def profile():
    users = list(mongo.db.users.find())
    books = list(mongo.db.books.find())
    return render_template('profile.html', users=users, books=books)



@app.route('/signup/', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"email.email": request.form.get('email')})

        if existing_user:
            flash("An account with this email already exists")
            return redirect(url_for("signup"))

        register = {
            "name": request.form.get("name").lower(),
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # Add new user
        session["user"] = request.form.get("email")
        flash("Registration Successful!")
        return redirect(url_for("profile", email=session["user"]))
    return render_template("signup.html")


@app.route('/login/', methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"email.email": request.form.get('email')})

    return render_template('login.html')


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
