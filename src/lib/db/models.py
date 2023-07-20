import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


class CreateUpdateMixin:
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.utcnow)


class User(CreateUpdateMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)


class Post(CreateUpdateMixin, db.Model):
    __tablename__ = 'post'

    id = db.Column(db.BigInteger, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship("User", backref=backref("posts", uselist=False))
    slug = db.Column(db.String, unique=True, nullable=False)
    key = db.Column(db.String, unique=True, nullable=False)

    text = db.Column(db.Text)

    @staticmethod
    def generate_slug():
        """Generate a slug for the post.

        Algorithm may be any.
        It is used uuid for simplifying
        """

        return str(uuid.uuid4())


class Comment(CreateUpdateMixin, db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.BigInteger, primary_key=True)
    post_id = db.Column(db.BigInteger, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship("Post", backref=backref("comments", uselist=False))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship("User", backref=backref("comments", uselist=False))
    text = db.Column(db.Text, nullable=False)
    key = db.Column(db.String, unique=True, nullable=False)
    slug = db.Column(db.String, unique=True, nullable=False)

    @staticmethod
    def generate_slug():
        """Generate a slug for the post.

        Algorithm may be any.
        It is mocked with uuid for simplifying
        """

        return str(uuid.uuid4())
