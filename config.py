import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	DEBUG = False
	TESTING = False
	CSRF_ENABLED = True
	SECRET_KEY = os.environ['SECRET_KEY']
	HUE_KEY = os.environ['HUE_KEY']
	USER_NAME = os.environ['USER_NAME']
	USER_PASS = os.environ['USER_PASS']
	DATABASE_URL = os.environ['DATABASE_URL']
	USE_RELOADER = False

class ProductionConfig(Config):
	DEBUG = False


class DevelopmentConfig(Config):
	DEVELOPMENT = True
	DEBUG = True
	USE_RELOADER = False


class TestingConfig(Config):
	TESTING = True