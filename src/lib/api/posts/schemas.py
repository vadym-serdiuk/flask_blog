from flask_restful import fields
from flask_restful.reqparse import RequestParser

from lib.api.fields import DetailApiUrl

user = {
    'full_name': fields.String,
    'link':  DetailApiUrl('users.userapi', 'username', 'username'),
}


comment_fields = {
    'post': fields.Nested({
        'created': fields.DateTime,
        'link': DetailApiUrl('posts.postsapi', 'slug', 'slug'),
    }),
    'slug': fields.String,
    'user': fields.Nested(user),
    'text': fields.String,
    'created': fields.DateTime,
}

post_fields = {
    'slug': fields.String,
    'author': fields.Nested(user),
    'text': fields.String,
    'created': fields.DateTime,
    'link': DetailApiUrl('posts.postsapi', 'slug', 'slug'),
}


post_create_parser = RequestParser()
post_create_parser.add_argument('text', required=True, type=str)
post_create_parser.add_argument('key', required=True, type=str)

comment_add_parser = RequestParser()
comment_add_parser.add_argument('text', required=True, type=str)
comment_add_parser.add_argument('key', required=True, type=str)

pagination_parser = RequestParser()
pagination_parser.add_argument('page', location='args', type=int, default=1)
