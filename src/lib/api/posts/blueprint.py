from flask import Blueprint, session, current_app
from flask_restful import Resource, Api, marshal
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from werkzeug.exceptions import BadRequest

from lib.api.authentication import login_required
from lib.db.models import db, Comment
from lib.api.errors import Error
from lib.api.posts.schemas import post_create_parser, pagination_parser, post_fields, comment_fields, comment_add_parser
from lib.db.models import Post

posts_bp = Blueprint('posts', __name__)
post_api = Api(posts_bp)


class PostsAPI(Resource):

    @login_required
    def put(self):
        try:
            args = post_create_parser.parse_args()
        except BadRequest as e:
            return Error('bad_request', e.data['message'], 400)

        user = session['user']
        try:
            post = Post(author_id=user['id'], text=args.text, key=args.key, slug=Post.generate_slug())
            db.session.add(post)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            post = db.session.execute(
                db.select(Post).where(Post.author_id == user['id'], Post.key == args.key)
            ).scalar_one()
            return {'data': marshal(post, post_fields)}, 200

        return {'data': marshal(post, post_fields)}, 201

    @login_required
    def get(self, slug=None):
        if slug is None:
            return self.get_list()
        else:
            post = Post.query.options(joinedload(Post.author)).filter_by(slug=slug).first()
            return {'data': marshal(post, post_fields)}

    def get_list(self):
        page_args = pagination_parser.parse_args()
        query = Post.query.options(joinedload(Post.author))
        posts = db.paginate(query, page=page_args.page, per_page=current_app.config['POSTS_PER_PAGE'])
        return {'data': [marshal(data, post_fields) for data in posts.items],
                'has_next': posts.has_next,
                'has_prev': posts.has_prev}


class CommentsAPI(Resource):

    @login_required
    def put(self, post_slug):
        post = Post.query.filter_by(slug=post_slug).first()
        if not post:
            return Error('not_found', 'Post Not Found', 404)

        args = comment_add_parser.parse_args()
        # check the existing
        comment = Comment.query.filter_by(post=post, key=args.key).first()
        if comment:
            return {'data': marshal(comment, comment_fields)}, 200

        comment = Comment(user_id=session['user']['id'],
                          text=args.text,
                          key=args.key,
                          post_id=post.id,
                          slug=Comment.generate_slug())
        db.session.add(comment)
        db.session.commit()
        return {'data': marshal(comment, comment_fields)}, 201

    @login_required
    def get(self, post_slug=None, slug=None):
        if post_slug and not slug:
            return self.get_list(post_slug)
        else:
            post = (Comment.query.options(joinedload(Comment.post), joinedload(Comment.user))
                    .filter_by(slug=slug).first())
            return {'data': marshal(post, post_fields)}

    def get_list(self, post_slug):
        page_args = pagination_parser.parse_args()
        query = Comment.query.options(joinedload(Comment.post), joinedload(Comment.user))
        comments = db.paginate(query, page=page_args.page, per_page=current_app.config['COMMENTS_PER_PAGE'])
        return {'data': [marshal(data, comment_fields) for data in comments.items],
                'has_next': comments.has_next,
                'has_prev': comments.has_prev}


post_api.add_resource(PostsAPI, '/posts', '/posts/<slug>')
post_api.add_resource(CommentsAPI, '/posts/<post_slug>/comments', '/comments/<slug>')
