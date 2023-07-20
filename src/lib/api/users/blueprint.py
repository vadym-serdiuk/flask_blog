from flask import Blueprint, session
from flask_restful import Resource, Api, marshal
from sqlalchemy import exists
from sqlalchemy.exc import NoResultFound
from werkzeug.security import generate_password_hash, check_password_hash

from lib.api.authentication import login_required
from lib.api.users.schemas import user_create_parser, user_login_parser, user_fields
from lib.api.errors import Error
from lib.db.models import db, User

users_bp = Blueprint('users', __name__)
api = Api(users_bp)


class UserAPI(Resource):
    def post(self):
        """It should be a throttling here"""

        args = user_create_parser.parse_args()
        user_exists = db.session.query(exists().where(User.username == args.username)).scalar()
        if user_exists:
            return Error('duplicated', 'User with this username already exists', 400)

        user = User(username=args.username, password=generate_password_hash(args.password), full_name=args.full_name)
        db.session.add(user)
        db.session.commit()
        return {'status': 'Created'}, 201

    @login_required
    def get(self, username):
        try:
            user = db.session.execute(db.select(User).where(User.username == username)).scalar_one()
        except NoResultFound:
            return Error('not_found', 'Not found', 404)
        return marshal(user, user_fields)


class LoginAPI(Resource):
    def post(self):

        try:
            args = user_login_parser.parse_args()
        except Exception as e:
            return Error('bad_request', e.data['message'], 400)
        else:
            try:
                user = db.session.execute(db.select(User).where(User.username == args.username)).scalar_one()
            except NoResultFound:
                pass
            else:
                if check_password_hash(user.password, args.password):
                    self.save_session(user)
                    return {'status': 'Ok'}, 200

        return Error('wrong_credentials', 'Username or password are incorrect', 400)

    def save_session(self, user: User):
        session['user'] = {'id': user.id, 'username': user.username, 'full_name': user.full_name}


class LogoutAPI(Resource):
    def post(self):
        session.pop('user', None)
        return {'status': 'Ok'}, 200


api.add_resource(UserAPI, '/users')
api.add_resource(LoginAPI, '/auth/login')
api.add_resource(LogoutAPI, '/auth/logout')
