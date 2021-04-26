import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
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
@app.route("/home", methods=["GET", "POST"])
def home():
    books = list(mongo.db.books.find())
    featured_books()
    return render_template('index.html', books=books)


# render featured books to homepage from database
# Data base is filled with info from Google Books API
@app.route("/featured_books")
def featured_books():
    books = mongo.db.books.find()
    for book in books:
        if (book["image"] == ""):
            isbn = book["isbn"]
            isbn_book_url = ISBN_SEARCH_BASE_URL + isbn

            try:
                response = requests.get(isbn_book_url)
                response.raise_for_status()
                j_response = response.json()
                for x in range(1):
                    cover_img = j_response['items'][x]['volumeInfo']['imageLinks']['thumbnail']
                    vol_id = j_response['items'][x]['id']
                    author = j_response['items'][x]['volumeInfo']['authors']
                    title = j_response['items'][x]['volumeInfo']['title']
                    genre = j_response['items'][x]['volumeInfo']['categories']
                    link = j_response['items'][x]['volumeInfo']['infoLink']
                    str_cover = str(cover_img)
                    str_isbn = str(isbn)
                    str_id = str(vol_id)
                    str_author = str(author)
                    str_title = str(title)
                    str_genre = str(genre)
                    str_link = str(link)

                    mongo.db.books.update_one(
                        {'isbn': str_isbn},
                        {'$set':
                            {
                                'image': str_cover,
                                'volume_id': str_id,
                                'author': str_author,
                                'title': str_title,
                                'genre': str_genre,
                                'book_link': str_link
                            }
                        }
                    )

            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                return render_template('index.html')

            except Exception as err:
                print(f'Other error occurred: {err}')
                return render_template('index.html')


# Searches google books API and renders info to search page
@app.route("/get_search", methods=["GET", "POST"])
def getSearch():
    getreq_url = SEARCH_BASE_URL + request.form.get("search")
    print(getreq_url)
    r = requests.get(url = getreq_url)
    data = r.json()
    print(data)

    return render_template('search_results.html', books=data)


# update user library from search or featured books
# @app.route("/update_library")
# def update_library():
#     if session['email']:




# Render user profile if user in session
@app.route("/profile/", methods=["GET", "POST"])
def profile():
    if session['email']:
        user = mongo.db.users.find_one(
            {"email": session["email"]})
        user_library = mongo.db.user_books.find()

    return render_template('profile.html', user=user, books=user_library)


# Update user profile with user image and bio
# Still requires work
@app.route("/update_profile/", methods=["GET", "POST"])
def update_profile():
    user_bio = mongo.db.users.find_one(
            {"email": session["email"]})["bio8"]
    if request.method == "POST":
        if session['email']:
            profile_image = request.form.get('image')
            user_image = str(profile_image)
            mongo.db.users.update_one(
                        {'email': session['email']},
                        {'$set':
                            {
                                'image': user_image,
                                'bio': request.form.get('bio-update')
                            }
                        }
                    )
            flash("Profile updated")
            return redirect(url_for("profile"))
    return render_template('update_profile.html', user_bio=user_bio)


# Creating and adding a new user to DB
# exisiting_user needs to be fisxed...
@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"email": request.form.get('email')})

        if existing_user:
            flash("An account with this email already exists")
            return redirect(url_for("signup"))

        else:
            register = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "password": generate_password_hash(
                        request.form.get("password")),
                "bio": " "
                                    }
            users_books = {
                "email": request.form.get("email")
            }
            mongo.db.users.insert_one(register)
            mongo.db.user_books.insert_one(users_books)

            # Add new user
            session["email"] = request.form.get("email")
            flash("Registration Successful!")
            return redirect(url_for("profile", email=session["email"]))
    return render_template("signup.html")


# Login to user profile with encrypted password and email
@app.route('/login', methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"email": request.form.get('email').lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                session["email"] = request.form.get("email").lower()
                flash("Welcome, {}".format(
                    request.form.get("email")))
                return redirect(url_for("profile"))
            else:
                # invalid password match
                flash("Incorrect Email and/or Password")
                return redirect(url_for("log_in"))

        else:
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("log_in"))

    return render_template("login.html")


@app.route("/logout")
def log_out():
    # remove user from session cookie
    flash("See you soon!")
    session.pop("email")
    return redirect(url_for("log_in"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
