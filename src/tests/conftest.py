import re
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash

from app import get_config


@pytest.fixture()
def prepare_db(test_db_name):
    config = get_config()
    db_uri = config["SQLALCHEMY_DATABASE_URI"]
    postgres_db = re.sub(r'(.*?)/(\w+)$', r'\1/postgres', db_uri)
    engine = create_engine(postgres_db)
    with engine.connect() as conn:
        try:
            conn.execution_options(isolation_level="AUTOCOMMIT").execute(text(f'DROP DATABASE IF EXISTS {test_db_name};'))
        except Exception as e:
            conn.rollback()
        else:
            conn.commit()

        conn.execute(text(f'CREATE DATABASE {test_db_name}'))
        conn.commit()


@pytest.fixture
def app(test_db_name, prepare_db):
    from app import get_app

    config = get_config()
    config['TESTING'] = True
    db_uri = config['SQLALCHEMY_DATABASE_URI']
    test_db_uri = re.sub(r'(.*?)/(\w+)$', fr'\1/{test_db_name}', db_uri)
    config['SQLALCHEMY_DATABASE_URI'] = test_db_uri

    app_instance = get_app(config)
    with app_instance.test_request_context():
        yield app_instance


@pytest.fixture(autouse=True)
def db(app, test_db_name):
    from lib.db.models import db

    db.create_all()
    db.session.commit()
    yield db

    db.session.rollback()
    db.session.close()
    db.engine.dispose()


@pytest.fixture
def test_db_name():
    return 'test_blog'


@pytest.fixture
def user():
    return Mock(username='test_user', password='test_password', full_name='Test User')


@pytest.fixture
def dbuser(db, user):
    from lib.db.models import User

    new_user = User(username=user.username, password=generate_password_hash(user.password), full_name=user.full_name)
    db.session.add(new_user)
    db.session.commit()
    return new_user


@pytest.fixture
def auth_client(app, dbuser):
    client = app.test_client()
    with client.session_transaction() as session:
        session['user'] = {'id': dbuser.id, 'username': dbuser.username, 'full_name': dbuser.full_name}
    yield client
