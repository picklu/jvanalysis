from os import environ, listdir, path

CURRENT_PATH = path.dirname(path.abspath(__file__))
DATA_PATH = path.join(CURRENT_PATH, "jvanalysis/static/data")
SECRET_PATH = path.join(CURRENT_PATH, "secret.key")
SAMPLE_DATA_PATH = path.join(DATA_PATH, "sample_data.txt")

class Config(object):
    """Base config class"""
    DATA_FILES = sorted(listdir(DATA_PATH))
    DATABASE = "jvanalysis"
    DEBUG = True
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = False
    TESTING = False
    GUEST_USER_EMAIL = environ.get('GUEST_ID')
    GUEST_USER_PASSWORD = environ.get('GUEST_PASSWORD')
    SAMPLE_DATA = SAMPLE_DATA_PATH
    SECRET_KEY = 'A really secret string generated randomly'
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = None
    SESSION_MONGODB_DB = 'jvanalysis_session'
    SESSION_MONGODB_COLLECT = 'session'
    SESSION_KEY_PREFIX = 'jV'
    URI_MONGODB = environ.get('MONGODB_URI')


class ProductionConfig(Config):
    """Production specific config"""
    DEBUG = False
    SECRET_KEY = open(SECRET_PATH).read()

class DevelopmentConfig(Config):
    """Development environment specific config"""
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'localhost:27017'
    SECRET_KEY = 'd908eb90af7ac0e79c2c61b8fe60c33e'