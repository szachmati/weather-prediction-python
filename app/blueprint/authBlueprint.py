from json import dumps
from flask import Blueprint, request, Response
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..dto import UserLoginDTO
from ..main import db, jwt
from ..mapper import map_to_user_dto
from ..model import User
from ..utils import json_to_object

authentication = Blueprint("auth", __name__)


@authentication.route("/signup", methods=["POST"])
def signup():
    user: User = json_to_object(request.data)
    if db.users.find_one({"email": user.email}) is not None:
        return Response(status=409, response=dumps({"error": "User with given email already exists"}))
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


@authentication.route("/user", methods=["GET"])
@jwt_required
def user_info():
    return get_jwt_identity


@jwt.unauthorized_loader
def unauthorized_handler(callback):
    return Response(status=401, response=dumps({"error": callback}))


