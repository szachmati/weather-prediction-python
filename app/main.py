import datetime
from flask import Flask, Response, request
from flask_cors import CORS
from pymongo import MongoClient
from .utils import json_to_object
from .model import User
from .dto import UserLogin
from .mapper.userMapper import map_to_user_dto
from .utils.settings import MONGO_URL, JWT_SECRET_KEY
from json import dumps
from flask_jwt_extended import JWTManager, create_access_token
from flask_bcrypt import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# app config
client = MongoClient(MONGO_URL)
db = client.weather_db
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)
jwt = JWTManager(app)


@app.route('/api/signup', methods=['POST'])
def signup():
    print(request.data)
    user: User = json_to_object(request.data)
    if db.users.find_one({"email": user.email}) is not None:
        return Response(response=dumps({"error": "User with given email already exists"}), status=409)
    user.password = generate_password_hash(user.password)
    db.users.insert_one(user.__dict__)
    return Response(status=200, response=dumps({"message": "Registration completed successfully"}))


@app.route('/api/signin', methods=['POST'])
def signin():
    user_credentials: UserLogin = json_to_object(request.data)
    user = db.users.find_one({"email": user_credentials.email})
    if user is not None and check_password_hash(user["password"], user_credentials.password):
        user_dto = map_to_user_dto(user)
        access_token = create_access_token(identity=user_dto.__dict__)
        return Response(status=200, response=dumps({"access_token": access_token}))
    elif user is not None and not check_password_hash(user["password"], user_credentials.password):
        return Response(status=400, response=dumps({"error": "Invalid user credentials"}))
    else:
        return Response(status=400, response=dumps({"error": "Provide correct email and password"}))


@app.route('/api/info')
def hello_world():
    return {
        "user": "Mati",
        "title": "Title"
    }


if __name__ == '__main__':
    app.run()
