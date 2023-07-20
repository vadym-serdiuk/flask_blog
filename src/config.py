import os

from dotenv import load_dotenv


load_dotenv()

SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URI', 'postgresql://pguser:pgpass@database.docker.local/blog')

SECRET_KEY = 'change me'

POSTS_PER_PAGE = 50
COMMENTS_PER_PAGE = 10
