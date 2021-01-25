import datetime
from flask import Flask, Response, request
from flask_cors import CORS
from flask_bcrypt import generate_password_hash
from pymongo import MongoClient
from .utils import deserialize_json
from .model import User, UserLogin
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
    if db.users.find_one({"email": user.email}) is not None:
        return Response(response=dumps({"error": "User with given email already exists"}), status=409)
    db.users.insert_one({
        "name": user.name,
        "surname": user.surname,
        "email": user.email,
        "password": user.password  # tutaj jakiś bcrypt by się przydał :p
    })
    return Response(status=200, response=dumps({"message": "Registration completed successfully"}))


# na razie mock
@app.route('/api/signin', methods=['POST'])
def signin():
    user_credentials: UserLogin = deserialize_json(request.data)
    if db.users.find_one({"email": user_credentials.email}) is not None:
        return Response(status=200, response=dumps({
            "message": "Login was successful",
            "user": {
                "email": user_credentials.email,
                "password": user_credentials.password
            }
        }))
    return None


@app.route('/api/info')
def hello_world():
    return {
        "user": "Mati",
        "title": "Title"
    }


if __name__ == '__main__':
    app.run()
