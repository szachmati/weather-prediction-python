import datetime
from flask import Flask, Response, request
from flask_cors import CORS
from pymongo import MongoClient
from .utils import deserialize_json
from .model import User
from .utils.settings import MONGO_URL, JWT_SECRET_KEY
from json import dumps

app = Flask(__name__)
CORS(app)

# app config
client = MongoClient(MONGO_URL)
db = client.weather_db
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


@app.route('/api/signup', methods=['POST'])
def signup():
    user: User = deserialize_json(request.data)
    if db.users.find_one({"email": user.name}) is not None:
        return Response(response=dumps({"error": "User with given email already exists"}), status=409)
    db.users.insert_one({
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": user.password  # tutaj jakiś bcrypt by się przydał :p
    })
    return Response(status=200, response=dumps({"message": "Registration completed successfully"}))


@app.route('/api/hello-world')
def hello_world():
    return {
        "user": "Mati",
        "title": "Title"
    }


if __name__ == '__main__':
    app.run()
