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
                cover_img = j_response['items'][0]['volumeInfo']['imageLinks']['thumbnail']
                vol_id = j_response['items'][0]['id']
                author = j_response['items'][0]['volumeInfo']['authors']
                title = j_response['items'][0]['volumeInfo']['title']
                genre = j_response['items'][0]['volumeInfo']['categories']
                link = j_response['items'][0]['volumeInfo']['infoLink']
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
def get_search():
    getreq_url = SEARCH_BASE_URL + request.form.get("search")
    print(getreq_url)
    r = requests.get(url = getreq_url)
    data = r.json()

    return render_template('search_results.html', books=data)


# update user library from search or featured books
@app.route("/library/<vol_id>", methods=["GET", "POST"])
def library(vol_id):
    if session['email']:
        id_book_url = SEARCH_BASE_URL + vol_id

    try:
        response = requests.get(id_book_url)
        response.raise_for_status()
        j_response = response.json()
        cover_img = j_response['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        author = j_response['items'][0]['volumeInfo']['authors']
        title = j_response['items'][0]['volumeInfo']['title']
        genre = j_response['items'][0]['volumeInfo']['categories']
        link = j_response['items'][0]['volumeInfo']['infoLink']
        str_cover = str(cover_img)
        str_id = str(vol_id)
        str_author = str(author)
        str_title = str(title)
        str_genre = str(genre)
        str_link = str(link)

        mongo.db.user_books.insert_one(
            {'email': session['email'],
             'image': str_cover,
             'volume_id': str_id,
             'author': str_author,
             'title': str_title,
             'genre': str_genre,
             'book_link': str_link
            }
        )

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        flash('An error occurred in processing your request. Please try again.')
        return render_template('index.html')

    except Exception as err:
        print(f'Other error occurred: {err}')
        flash('An error occurred in processing your request. Please try again.')
        return render_template('index.html')

    else:
        flash("Login to add to library")
        redirect(url_for('log_in', _external=True, _scheme='https'))

    return redirect(url_for('profile', _external=True, _scheme='https'))


@app.route('/remove_book/<book_id>')
def remove_book(book_id):
    mongo.db.user_books.remove({"_id": ObjectId(book_id)})

    return redirect(url_for('profile', _external=True, _scheme='https'))


# Render user profile if user in session
@app.route("/profile/", methods=["GET", "POST"])
def profile():
    if session['email']:
        if mongo.db.users.find_one(
                {'email': session['email']}):
            user = mongo.db.users.find_one(
                    {'email': session['email']})
            books = mongo.db.user_books.find()

            for book in books:
                if (book["email"] == session['email']):
                    user_books = books

                    return render_template('profile.html', user=user, books=user_books)

        else:
            flash("Login to add to library")
            redirect(url_for('log_in', _external=True, _scheme='https'))


@app.route("/reviews/", methods=["GET", "POST"])
def reviews():
    reviews = mongo.db.book_reviews.find()
    return render_template('submit_review.html', reviews=reviews)


@app.route("/book_review/<vol_id>", methods=["GET", "POST"])
def book_review(vol_id):
    getreq_url = SEARCH_BASE_URL + vol_id
    r = requests.get(url = getreq_url)
    data = r.json()
    reviews = list(mongo.db.book_reviews.find())

    return render_template('book_review.html', reviews=reviews,
                           book=data, vol_id=vol_id,)


@app.route("/add_reviews/<vol_id>", methods=["GET", "POST"])
def add_reviews(vol_id):
    id_book_url = SEARCH_BASE_URL + vol_id
    if request.method == 'POST':
        user_name = mongo.db.users.find_one(
                    {'email': session['email']})['name']
    try:
        response = requests.get(id_book_url)
        response.raise_for_status()
        j_response = response.json()
        cover_img = j_response['items'][0]['volumeInfo']['imageLinks']['thumbnail']
        link = j_response['items'][0]['volumeInfo']['infoLink']
        str_cover = str(cover_img)
        str_id = str(vol_id)
        str_link = str(link)

        mongo.db.book_reviews.insert_one(
            {'email': session['email'],
             'name': user_name,
             'image': str_cover,
             'volume_id': str_id,
             'book_link': str_link,
             'rating': request.form.get('rating'),
             'comment': request.form.get('comment')
            }
        )

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        flash('An error occurred in processing your request. Please try again.')
        return render_template('reviews')

    except Exception as err:
        print(f'Other error occurred: {err}')
        flash('An error occurred in processing your request. Please try again.')
        return render_template('reviews')
        
    return redirect(url_for('book_review', vol_id=vol_id))


# Update user profile with user image and bio
# Still requires work
@app.route("/update_profile/", methods=["GET", "POST"])
def update_profile():
    user_bio = mongo.db.users.find_one_or_404(
            {"email": session["email"]})["bio"]
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
            return redirect(url_for("profile", _external=True, _scheme='https'))
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
            return redirect(url_for("signup", _external=True, _scheme='https'))

        else:
            register = {
                "name": request.form.get("name"),
                "email": request.form.get("email"),
                "password": generate_password_hash(
                        request.form.get("password")),
                "bio": " "
                                    }
            mongo.db.users.insert_one(register)

            # Add new user
            session["email"] = request.form.get("email")
            flash("Registration Successful!")
            return redirect(url_for("profile", _external=True, _scheme='https'))
    return render_template("signup.html")


# Login to user profile with encrypted password and email
@app.route('/login', methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
                {"email": request.form.get('email').lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["email"] = request.form.get("email").lower()
                flash("Welcome, {}".format(request.form.get("email")))
                return redirect(url_for("profile", _external=True, _scheme='https'))
                # redirect("/profile/")
            else:
                print("GOT HERE CHECK PASS ELSE")
                # invalid password match
                flash("Incorrect Email and/or Password")
                return redirect(url_for("log_in", _external=True, _scheme='https'))

        else:
            print("GOT HERE FIRST ELSE")
            # username doesn't exist
            flash("Incorrect Email and/or Password")
            return redirect(url_for("log_in", _external=True, _scheme='https'))

    return render_template("login.html")


@app.route("/logout")
def log_out():
    # remove user from session cookie
    flash("See you soon!")
    session.pop("email")
    return redirect(url_for("log_in", _external=True, _scheme='https'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)