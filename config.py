import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = 'app/static/photos/'
    DB_NAME = 'doma_db'
    DB_USER = 'sakaf'
    USER_PASSWORD = '1527'
    DB_HOST = 'localhost'
    DB_PORT = 5432