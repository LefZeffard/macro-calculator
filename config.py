import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-only-fallback'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:Heyaman$4$$@localhost:5432/macros'
    SQLALCHEMY_TRACK_MODIFICATIONS = False