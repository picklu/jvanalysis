from os import environ, path

class Config(object):
    """Base config class"""
    DATA_PATH = path.join(path.dirname(__file__), "jvanalysis/static/data")
    DATABASE = "jvanalysis"
    DEBUG = True
    TESTING = False
    GUEST_USER_EMAIL = environ.get('GUEST_ID')
    GUEST_USER_PASSWORD = environ.get('GUEST_PASSWORD')
    SAMPLE_DATA = "sample_data.txt"
    SECRET_KEY = 'A really secret string generated randomly'
    SESSION_TYPE = 'mongodb'
    SESSION_MONGODB = None
    SESSION_MONGODB_DB = 'jvanalysis_session'
    SESSION_MONGODB_COLLECT = 'session'
    SESSION_KEY_PREFIX = 'jV'
    SESSION_PERMANENT = True
    SESSION_USE_SIGNER = False

class ProductionConfig(Config):
    """Production specific config"""
    DEBUG = False
    SECRET_KEY = open('secret.key').read()

class DevelopmentConfig(Config):
    """Development environment specific config"""
    # DATABASE = None
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'd908eb90af7ac0e79c2c61b8fe60c33e'