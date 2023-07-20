import random
import uuid

import pytest
from sqlalchemy import exists

from lib.api.posts.blueprint import post_api, PostsAPI, CommentsAPI
from lib.db.models import Post, User, Comment


@pytest.fixture
def new_post_data():
    return {'text': 'new post text', 'key': str(uuid.uuid4())}


@pytest.fixture
def authors(db):
    authors_list = []
    for num in range(5):
        user = User(username=f'user_{num}', password='pass', full_name=f'Author {num}')
        db.session.add(user)
        authors_list.append(user)
    db.session.commit()
    return authors_list


@pytest.fixture
def existing_posts(db, authors):
    posts = []
    for num in range(9):
        author = random.choice(authors)
        post = Post(author_id=author.id, text=f'some text {num}', key=str(uuid.uuid4()),
                    slug=Post.generate_slug())
        db.session.add(post)
        posts.append(post)
    db.session.commit()
    return posts


@pytest.fixture
def post_with_comments(db, authors):
    post_author = authors[0]
    post = Post(author_id=post_author.id, text=f'some text', key=str(uuid.uuid4()),
                slug=Post.generate_slug())

    db.session.add(post)
    db.session.commit()
    for num in range(9):
        comment_author = random.choice(authors)
        comment = Comment(user_id=comment_author.id,
                          text=f'some text {num}',
                          key=str(uuid.uuid4()),
                          post_id=post.id,
                          slug=Post.generate_slug())
        db.session.add(comment)
    db.session.commit()
    return post


class TestPosts:
    def test_create_post__error__unauthenticated(self, app, db, new_post_data):
        client = app.test_client()
        url = post_api.url_for(PostsAPI)
        response = client.put(url, json=new_post_data)
        assert response.status_code == 401

    def test_create_post__success(self, auth_client, db, new_post_data):
        url = post_api.url_for(PostsAPI)
        response = auth_client.put(url, json=new_post_data)
        assert response.status_code == 201
        assert db.session.query(exists().where(Post.key == new_post_data['key'])).scalar()

    def test_create_post__error__duplicate(self, auth_client, db, new_post_data):
        url = post_api.url_for(PostsAPI)
        response1 = auth_client.put(url, json=new_post_data)
        assert response1.status_code == 201
        response2 = auth_client.put(url, json=new_post_data)
        assert response2.status_code == 200

    def test_posts_list__success(self, auth_client, existing_posts, monkeypatch, app):
        monkeypatch.setitem(app.config, 'POSTS_PER_PAGE', 5)
        url = post_api.url_for(PostsAPI)
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.json['data']) == 5
        assert response.json['has_next'] is True
        assert response.json['has_prev'] is False

        url += '?page=2'
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.json['data']) == 4
        assert response.json['has_next'] is False
        assert response.json['has_prev'] is True

    def test_posts_single__success(self, auth_client, existing_posts, monkeypatch, app):
        monkeypatch.setitem(app.config, 'POSTS_PER_PAGE', 5)
        url = post_api.url_for(PostsAPI, slug=existing_posts[0].slug)
        response = auth_client.get(url)
        assert response.status_code == 200


class TestComments:

    def test_comments_list__success(self, auth_client, post_with_comments, monkeypatch, app):
        monkeypatch.setitem(app.config, 'COMMENTS_PER_PAGE', 5)
        url = post_api.url_for(CommentsAPI, post_slug=post_with_comments.slug)
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.json['data']) == 5
        assert response.json['has_next'] is True
        assert response.json['has_prev'] is False

        url += '?page=2'
        response = auth_client.get(url)
        assert response.status_code == 200
        assert len(response.json['data']) == 4
        assert response.json['has_next'] is False
        assert response.json['has_prev'] is True

    def test_comments_add__success(self, auth_client, post_with_comments):
        url = post_api.url_for(CommentsAPI, post_slug=post_with_comments.slug)
        comment_data = {
            'text': 'comment 000',
            'key': 'key 012345'
        }
        response = auth_client.put(url, json=comment_data)
        assert response.status_code == 201, response.json
