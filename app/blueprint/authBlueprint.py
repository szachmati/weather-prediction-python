from json import dumps

from flask import Blueprint, request, Response
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token


from ..dto import UserLoginDTO
from ..main import db
from ..mapper import map_to_user_dto
from ..model import User
from ..utils import json_to_object

authentication = Blueprint("auth", __name__)


@authentication.route("/signup", methods=["POST"])
def signup():
    print(request.data)
    user: User = json_to_object(request.data)
    if db.users.find_one({"email": user.email}) is not None:
        return Response(response=dumps({"error": "User with given email already exists"}), status=409)
    user.password = generate_password_hash(user.password)
    db.users.insert_one(user.__dict__)
    return Response(status=200, response=dumps({"message": "Registration completed successfully"}))


@authentication.route('/signin', methods=['POST'])
def signin():
    user_credentials: UserLoginDTO = json_to_object(request.data)
    user = db.users.find_one({"email": user_credentials.email})
    if user is not None and check_password_hash(user["password"], user_credentials.password):
        user_dto = map_to_user_dto(user)
        access_token = create_access_token(identity=user_dto.__dict__, fresh=True)
        return Response(status=200, response=dumps({"access_token": access_token}))
    elif user is not None and not check_password_hash(user["password"], user_credentials.password):
        return Response(status=400, response=dumps({"error": "Invalid user credentials"}))
    else:
        return Response(status=400, response=dumps({"error": "Provide correct email and password"}))