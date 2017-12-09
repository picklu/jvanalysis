import os

class Config(object):
    """Base config class"""
    SECRET_KEY = 'A really secret string generated randomly'
    DEBUG = True
    TESTING = False
    GUEST_USER_EMAIL = os.environ.get('GUEST_ID')
    GUEST_USER_PASSWORD = os.environ.get('GUEST_PASSWORD')

class ProductionConfig(Config):
    """Production specific config"""
    DEBUG = False
    SECRET_KEY = open('secret.key').read()

class DevelopmentConfig(Config):
    """Development environment specific config"""
    DEBUG = True
    # TESTING = True
    SECRET_KEY = 'd908eb90af7ac0e79c2c61b8fe60c33e'