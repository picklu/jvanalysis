from os.path import dirname, join
secret_file = join(dirname(__file__), '../secret.key')

class Config(object):
    """Base config class"""
    SECRET_KEY = 'A really secret string generated randomly'
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production specific config"""
    DEBUG = False
    SECRET_KEY = open(secret_file).read()

class DevelopmentConfig(Config):
    """Development environment specific config"""
    DEBUG = True
    TESTING = True
    SECRET_KEY = 'd908eb90af7ac0e79c2c61b8fe60c33e'