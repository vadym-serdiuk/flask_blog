from unittest.mock import Mock

import pytest
from sqlalchemy import exists
from werkzeug.security import generate_password_hash

from lib.api.users.blueprint import UserAPI, api as auth_api, LogoutAPI, LoginAPI
from lib.db.models import User


@pytest.fixture
def new_user():
    return Mock(username='newuser', password='pass', full_name='Full name')


@pytest.fixture
def new_user_created(new_user, db):
    user = User(username=new_user.username, password=generate_password_hash(new_user.password), full_name=new_user.full_name)
    db.session.add(user)
    db.session.commit()
    return user


class TestAPIAuth:
    def test_create_user_success(self, app, db, new_user):
        url = auth_api.url_for(UserAPI)
        post_data = {'username': new_user.username,
                     'password': new_user.password,
                     'full_name': new_user.full_name}
        response = app.test_client().post(url, json=post_data)
        assert response.status_code == 201, response.json
        result = db.session.query(exists().where(User.username == new_user.username)).scalar()
        assert result

    def test_create_user__duplicate_error(self, app, db, new_user, new_user_created):
        url = auth_api.url_for(UserAPI)
        post_data = {'username': new_user.username,
                     'password': new_user.password,
                     'full_name': new_user.full_name}
        response = app.test_client().post(url, json=post_data)
        assert response.status_code == 400, response.json
        response_data = response.json
        assert response_data['error_code'] == 'duplicated'

    def test_login__success(self, app, dbuser, user):
        url = auth_api.url_for(LoginAPI)
        data = {'username': user.username, 'password': user.password}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 200, response.json

    def test_login__error__incorrect_user(self, app, dbuser):
        url = auth_api.url_for(LoginAPI)
        data = {'username': 'incorrect', 'password': dbuser.password}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 400, response.json
        assert response.json['error_code'] == 'wrong_credentials'

    def test_login__error__incorrect_password(self, app, dbuser):
        url = auth_api.url_for(LoginAPI)
        data = {'username': dbuser.username, 'password': 'incorrect'}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 400, response.json
        assert response.json['error_code'] == 'wrong_credentials'

    def test_login__error__no_password(self, app, dbuser):
        url = auth_api.url_for(LoginAPI)
        data = {'username': dbuser.username}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 400, response.json
        assert response.json['error_code'] == 'bad_request'

    def test_login__error__no_username(self, app, dbuser):
        url = auth_api.url_for(LoginAPI)
        data = {'password': dbuser.password}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 400, response.json
        assert response.json['error_code'] == 'bad_request'

    def test_login__error__empty_request(self, app, dbuser):
        url = auth_api.url_for(LoginAPI)
        data = {}
        response = app.test_client().post(url, json=data)
        assert response.status_code == 400, response.json
        assert response.json['error_code'] == 'bad_request'

    def test_logout__success(self, app, dbuser):
        url = auth_api.url_for(LogoutAPI)
        response = app.test_client().post(url)
        assert response.status_code == 200, response.content
