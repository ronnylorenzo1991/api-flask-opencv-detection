import os

class Config(object):
    SECRET_KEY = os.urandom(32)

# Grabs the folder where the script runs.
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_WEIGHTS_FOLDER = BASE_DIR + '/resources/weights/'
ALLOWED_WEIGHTS_EXTENSIONS = {'weights'}
UPLOAD_CFG_FOLDER = BASE_DIR + '/resources/config/'
ALLOWED_CFG_EXTENSIONS = {'cfg'}

class DevelopmentConfig(Config):
    DEBUG = True
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_BACKEND_URL = 'redis://localhost:6379/0'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:root@localhost/detection_api'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_POOL_TIMEOUT = 300

class ProductionConfig(Config):
    DEBUG = False

