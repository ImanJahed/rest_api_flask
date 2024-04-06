from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, create_refresh_token

from app.schema.schemas import UserSchema
from app.models import UserModel
from app.extensions import db
from app.blocklist import BLOCKLIST


blp = Blueprint("Users", "users", description="Operation on users")


@blp.route('/register')
class UserRegister(MethodView):
    """Register a user."""

    @blp.arguments(UserSchema)
    def post(self, user_data):

        if UserModel.query.filter(UserModel.username == user_data['username']).first():
            abort(409, message='User with that username already exists.')

        user = UserModel(
            username=user_data['username'],
            password=pbkdf2_sha256.hash(user_data['password'])
        )
        db.session.add(user)
        db.session.commit()

        return {'message': 'User Created'}, 201


@blp.route('/user/<int:user_id>')
class UserApi(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        return user

    @jwt_required()
    def delete(self, user_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        user = UserModel.query.get_or_404(user_id)

        db.session.delete(user)
        db.session.commit()

        return {'message': 'User deleted.'}, 204


@blp.route('/login')
class LoginUser(MethodView):

    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.username == user_data['username']).first()

        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            return {'access_token': access_token, 'refresh_token': refresh_token}, 200

        abort(401, message='Invalid Credential')


@blp.route('/logout')
class LogoutUser(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        print(get_jwt())
        return {'message': 'successfully logged out'}


@blp.route('/refresh')
class GetRefreshToken(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()

        new_token = create_access_token(current_user, fresh=False)

        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)

        return {'access_token': new_token}
