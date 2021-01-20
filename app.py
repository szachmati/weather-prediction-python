from types import SimpleNamespace

from flask import Flask, Response, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from json import loads, dumps

app = Flask(__name__)
CORS(app)

# mongo config
client = MongoClient('mongodb://localhost:27017/')
db = client.weather_db


class User():
    def __init__(self, name, surname, email, password):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password


def deserialize_json(json_object):
    return loads(json_object, object_hook=lambda d: SimpleNamespace(**d))


@app.route('/api/signup', methods=['POST'])
def signup():
    user: User = deserialize_json(request.data)
    print(user)
    # nie bangla if db.users.find({"email": user.name}):
    #     return Response(response=jsonify({"error": "User already exists"}), status=409, mimetype='application/json')
    db.users.insert_one({
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": user.password
    })
    return Response(mimetype='application/json', status=200)


@app.route('/api/hello-world')
def hello_world():
    return {
        "user": "Mati",
        "title": "Title"
    }


if __name__ == '__main__':
    app.run()
