from blacklist import BLACKLIST
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
)

from models.user import UserModel



BLANK_ERROR = "'{}' cannot be left blank."
NAME_ALREADY_EXISTS = "An user with name '{}' already exists"
ERROR_INSERTING = "An error occurred inserting user"
USER_NOT_FOUND = "User not found"
USER_CREATED = "User Created Successfully"
USER_DELETED = "User Successfully Deleted"
USER_LOGOUT = "Successfully loggged out."
INVALID_CREDENTIALS = "Invalid Credentials"



_user_parser = reqparse.RequestParser()
_user_parser.add_argument(
    "username", type=str, required=True, help=BLANK_ERROR.format("username")
)
_user_parser.add_argument(
    "password", type=str, required=True, help=BLANK_ERROR.format("password")
)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data["username"]):
            {"message": NAME_ALREADY_EXISTS.format(data["user"])}, 400

        try:
            user = UserModel(**data)
            user.save_to_db()
        except:
            return {"message": ERROR_INSERTING}          

        return {"message": USER_CREATED}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        return user.json()

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {"message": USER_DELETED}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        # get data from parser
        data = _user_parser.parse_args()
        # find user in db
        user = UserModel.find_by_username(data["username"])
        # check password -> `authenticate()`
        if user and safe_str_cmp(user.password, data["password"]):
            # create access token -> `identity()`
            access_token = create_access_token(identity=user.id, fresh=True)
            # create refresh token
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        return {"message": INVALID_CREDENTIALS}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jwt id
        BLACKLIST.add(jti)
        return {"message": USER_LOGOUT}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200
