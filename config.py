import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.secrets'))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-password2'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
      'sqlite:///' + os.path.join(basedir, 'data', 'app.db')
    DB2 = 'sqlite:///' + os.path.join(basedir, 'data', 'data.db')
    SQLALCHEMY_BINDS = {'data': DB2}
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER   = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = os.environ.get('ADMINS').split(',') if os.environ.get('ADMINS') else 'wesley.schaal@farmbio.uu.se'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
