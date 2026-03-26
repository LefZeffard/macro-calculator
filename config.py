import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-fallback'
    SQLALCHEMY_TRACK_MODIFICATIONS = False