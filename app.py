import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
if os.path.exists("env.py"):
    import env
#Routes
from user import routes


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SEKRET_KEY")

mongo = PyMongo(app)

API_KEY = os.environ.get('API_KEY')
SEARCH_BASE_URL = 'https://www.googleapis.com/books/v1/volumes?q='
VOLUME_BASE_URL = 'https://www.googleapis.com/books/v1/volumes/'

@app.route("/")
def register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
