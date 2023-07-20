import os

from flask import Flask, Config

from lib.api.users.blueprint import users_bp
from lib.api.posts.blueprint import posts_bp
from lib.db.models import db


def get_app(config):
    app = Flask(__name__)
    app.config = config

    db.init_app(app)
    app.db = db

    app.register_blueprint(users_bp)
    app.register_blueprint(posts_bp)
    return app


def get_config():
    config = Config(os.path.dirname(__file__), Flask.default_config)
    config.from_pyfile('config.py')
    return config


def main():
    config = get_config()
    app = get_app(config)
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
