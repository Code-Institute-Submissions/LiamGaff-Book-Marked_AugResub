from flask import Flask, jsonify


class User:

    def register(self):
        user = {
            "_id": "",
            "name": "",
            "email": "",
            "password": ""
        }

        return jsonify(user), 200