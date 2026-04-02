import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'moneta-dev-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///moneta.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False