from flask import Flask
from app import app
from user.models import User


@app.route('/user/signup', methods=["GET", "POST"])
def signup():
    return User().signup()