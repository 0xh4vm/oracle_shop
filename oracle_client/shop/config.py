import os
from datetime import timedelta
import cx_Oracle


basedir = os.path.abspath(os.path.dirname(__file__))
sid = cx_Oracle.makedsn('172.17.0.2', 1521, sid='XE')

class Config(object):
    DEBUG = True
    SECRET_KEY = 'gwkghkf2934ysfljb45efsjfhkadslg2'
    # SQLALCHEMY_DATABASE_URI = f'oracle://c##shop_user:orcl@{sid}'
    SQLALCHEMY_DATABASE_URI = f'oracle://c##empty_user:123@{sid}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'gwkghkf2934ysfljb45efsjfhkadslg212askjdqrdfh124'
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)

    UPLOADS_DEFAULT_DEST = f'{basedir}/app/static/users'