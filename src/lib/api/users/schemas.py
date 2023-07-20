from flask_restful import fields
from flask_restful.reqparse import RequestParser

from lib.api.fields import DetailApiUrl

user_create_parser = RequestParser()
user_create_parser.add_argument('username', required=True, type=str)
user_create_parser.add_argument('password', required=True, type=str)
user_create_parser.add_argument('full_name', required=True, type=str)

user_login_parser = RequestParser()
user_login_parser.add_argument('username', required=True, type=str)
user_login_parser.add_argument('password', required=True, type=str)


user_fields = {
    'link': DetailApiUrl('users.usersapi', 'username', 'username'),
    'full_name': fields.String,
}