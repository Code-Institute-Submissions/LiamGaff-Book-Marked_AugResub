import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from passlib.hash import pbkdf2_sha256
from bson.objectid import ObjectId
from requests.exceptions import HTTPError
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SEKRET_KEY")

mongo = PyMongo(app)

API_KEY = os.environ.get('API_KEY')
SEARCH_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q='
ISBN_SEARCH_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q=isbn:'
VOLUME_BASE_URL = 'https://www.googleapis.com/books/v1/volumes/'

@app.route("/")
def home():
    featured_books()
    books = list(mongo.db.books.find())
    return render_template('index.html', books=books)




def featured_books():
    books = mongo.db.books.find()
    for book in books:
        if (book["image"] == ""):
            isbn = book["isbn"]
            isbn_img_url = ISBN_SEARCH_BASE_URL + isbn
            print(isbn_img_url)

            try:
                response = requests.get(isbn_img_url)
                response.raise_for_status()
                j_response = response.json()
                for x in range(1):
                    cover_img = j_response['items'][x]['volumeInfo']['imageLinks']['thumbnail']
                    vol_id = j_response['items'][x]['id']
                    author = j_response['items'][x]['volumeInfo']['authors']
                    title = j_response['items'][x]['volumeInfo']['title']
                    genre = j_response['items'][x]['readingModes']['categories']
                    str_cover = str(cover_img)
                    str_isbn = str(isbn)
                    str_id = str(vol_id)
                    str_author = str(author)
                    str_title = str(title)
                    str_genre = str(genre)

                    mongo.db.books.update_one(
                        {'isbn': str_isbn},
                        {'$set':
                            {
                                'image': str_cover,
                                'volume_id': str_id,
                                'author': str_author,
                                'title': str_title,
                                'genre': str_genre
                            }
                        }
                    )

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return render_template('index.html')

            except Exception as err:
                print(f'Other error occurred: {err}')
                return render_template('index.html')
            return render_template('index.html')


@app.route("/getSearch", methods=["GET", "POST"])
def getSearch():
    books = list(mongo.db.books.find())
    isbn_getreq_url = ISBN_SEARCH_BASE_URL + request.form.get("search")
    print(isbn_getreq_url)
    r = requests.get(url = isbn_getreq_url)
    data = r.json()

    title = data['items'][0]['volumeInfo']['title']

    print(data)

    return render_template('index.html', books=books)

# Render user profile
@app.route("/profile/", methods=["GET", "POST"])
def profile():
    users = list(mongo.db.users.find())
    books = list(mongo.db.books.find())

    return render_template('profile.html', users=users, books=books,)


# Update user profile with user image and bio
# Still requires work
@app.route("/update_profile/", methods=["GET", "POST"])
def update_profile():
    if request.method == "POST":
        update_user = {
            "image": request.form.get("image"),
            "bio": request.form.get("bio-update")
        }
        mongo.db.user.update_one(update_user)
        flash("Profile updated")
        return redirect(url_for("profile"))
    return render_template('update_profile.html')


# Creating and adding a new user to DB
# exisiting_user needs to be fisxed...
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"user.email": request.form.get('email')})

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


# Login to user profile with encrypted password and email
@app.route('/login', methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"user.email": request.form.get('email')})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("email")
                flash("Welcome, {}".format(
                    request.form.get("email")))
                return redirect(url_for(
                    "profile", email=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Email and/or Password")
                return redirect(url_for("log_in"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("log_in"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
