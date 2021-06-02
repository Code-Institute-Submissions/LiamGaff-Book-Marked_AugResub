import os
import requests
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import Form, StringField, PasswordField, validators
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
@app.route('/home', methods=['GET', 'POST'])
def home():
    books = mongo.db.books.find()
    return render_template('index.html', books=books)


@app.route('/featured_books')
def featured_books():
    books = mongo.db.books.find()
    """ Searching books on the google books API by their ISBN
        and retrieving data which is then put into JSON format.
        The selected data is then used to populate the template.
    """
    for book in books:
        if (book['image'] == ""):
            isbn = book['isbn']
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
                """ Handle errors for request.
                """
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                flash('An error occurred in processing your request. Please try again.')
                return render_template('index.html')

            except Exception as err:
                print(f'Other error occurred: {err}')
                flash('An error occurred in processing your request. Please try again.')
                return render_template('index.html')


@app.route('/get_search', methods=['GET', 'POST'])
def get_search():
    """ Searches google books API by keywords and put data
        into JSON format to render data to search template.
    """
    getreq_url = SEARCH_BASE_URL + request.form.get('search')
    r = requests.get(url = getreq_url)
    data = r.json()

    return render_template('search_results.html', books=data)


@app.route('/library/<vol_id>', methods=['GET', 'POST'])
def library(vol_id):
    """ if user is in session, using the volume ID to search google
    books API and retrieve data which
    is put into JSON format to then copy to the user's profile/library.
    """
    if 'email' in session:
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

        """
        Return flashed message and redirect user if not logged in.
        """
    else:
        flash('Login to add to library')
        redirect(url_for('log_in', _external=True, _scheme='https'))

        return redirect(url_for('profile', _external=True, _scheme='https'))


@app.route('/remove_book/<book_id>')
def remove_book(book_id):
    """ Removing books from user database and render the profile template.
    """
    mongo.db.user_books.remove({'_id': ObjectId(book_id)})

    return redirect(url_for('profile', _external=True, _scheme='https'))


@app.route('/profile/', methods=['GET', 'POST'])
def profile():
    """ If user is in session retrieve user data from DB and render profile
        template. Retrieve users books from the database to populate their library.
    """
    if 'email' in session:
        user = mongo.db.users.find_one(
                {'email': session['email']})
        books = mongo.db.user_books.find()

        for book in books:
            if (book['email'] == session['email']):
                user_books = books

                return render_template('profile.html', user=user, books=user_books)
        """
        Redirect user to login if not in session.
        """

    else:
        flash('Login to profile')
        return redirect(url_for('log_in', _external=True, _scheme='https'))


@app.route('/reviews/', methods=['GET', 'POST'])
def reviews():
    """
    Retrieve reviews from the database and render them to the template.
    """
    reviews = mongo.db.book_reviews.find()
    return render_template('submit_review.html', reviews=reviews)


@app.route('/book_review/<vol_id>', methods=['GET', 'POST'])
def book_review(vol_id):
    """ Use volume ID to search API and put it into JSON format. 
        Display book data to review template.
    """
    getreq_url = VOLUME_BASE_URL + vol_id
    r = requests.get(url=getreq_url)
    r.raise_for_status()
    data = r.json()
    reviews = list(mongo.db.book_reviews.find())
    if 'email' in session:
        return render_template('book_review.html', reviews=reviews,
                               book=data, vol_id=vol_id)
    
    else:
        flash("Login to submit review")
        return render_template('book_review.html', reviews=reviews,
                               book=data, vol_id=vol_id)



@app.route('/add_reviews/<vol_id>', methods=['GET','POST'])
def add_reviews(vol_id):
    """ If user in session add users review to database if user has not
        already submitted a review for this volume ID. If user
        has already submitted a review for this title they will be
        redirected and flashed a warning message.
    """
    user = mongo.db.users.find_one({'email': session['email']})
    review = mongo.db.book_reviews.find({'volume_id': vol_id})
    if review['email'] == user:
        flash('You have already submitted a review for this book')
        return redirect(url_for('reviews'))
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
                'rating': str(request.form.get('rating')),
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


@app.route('/remove_review/<review_id>/<vol_id>')
def remove_review(review_id, vol_id):
    """ 
    Remove users review from the database
    """
    mongo.db.book_reviews.remove({'_id': ObjectId(review_id)})
    return redirect(url_for('book_review', vol_id=vol_id))


@app.route('/update_profile/', methods=['GET', 'POST'])
def update_profile():
    """ Update user profile User Image if user
        is in session. Not currently working.
    """
    if request.method == 'POST':
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
            flash('Profile updated')
            return redirect(url_for('profile', _external=True, _scheme='https'))
    return render_template('update_profile.html')


class signup_form(Form):
    name = StringField('', [
                validators.Length(min=4, max=25)])
    email = StringField('', [
                validators.Length(min=6, max=35),
                validators.DataRequired()])
    password = PasswordField('', [
                validators.DataRequired()])



@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    """ Call the signup_form class. Check if user has existing account.
        If no user exists with the profided email then
        generate an encrypted password and
        add users entered details to the database.
        Render user profile template.
    """
    form = signup_form(request.form)
    if request.method == 'POST' and form.validate():
        existing_user = mongo.db.users.find_one(
                {'email': form.email.data})

        if existing_user:
            flash('An account with this email already exists')
            return redirect(url_for('sign_up', _external=True, _scheme='https'))

        else:
            register = {
                'name': form.name.data, 
                'email': form.email.data,
                'password': generate_password_hash(form.password.data)
            }
            mongo.db.users.insert_one(register)
            

            # Add new user
            session['email'] = form.email.data
            flash('Registration Successful!')
            return redirect(url_for('profile'))
    return render_template('signup.html', form=form)


class login_form(Form):
    email = StringField('', [
                validators.DataRequired()])
    password = PasswordField('', [
                validators.DataRequired()])


@app.route('/login', methods=['GET', 'POST'])
def log_in():
    """ Call the login_form class. If user exists and the password matches
    the provided email then retrive use information and
        render profile template.
        Render and validate form.
    """
    form = login_form(request.form)
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one(
                {'email': form.email.data})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user['password'], request.form.get('password')):
                session['email'] = form.email.data
                return redirect(url_for('profile', _external=True, _scheme='https'))
                # redirect("/profile/")
            else:
                # invalid password match
                flash('Incorrect Email and/or Password')
                return redirect(url_for('log_in', _external=True, _scheme='https'))

        else:
            # username doesn't exist
            flash('Incorrect Email and/or Password')
            return redirect(url_for('log_in', _external=True, _scheme='https'))

    return render_template('login.html', form=form)


@app.route('/logout')
def log_out():
    # remove user from session cookie
    flash('See you soon!')
    session.pop('email')
    return redirect(url_for('log_in', _external=True, _scheme='https'))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)