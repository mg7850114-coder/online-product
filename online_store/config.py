import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'premium-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///premium_store.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    SESSION_PERMANENT = False
    SESSION_TYPE = 'filesystem'
    
    DEBUG = True
    PORT = 5000
    HOST = '0.0.0.0'