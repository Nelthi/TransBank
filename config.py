import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://neondb_owner:npg_epmB3rX6KuaD@ep-empty-mountain-a4sjb3xc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'azerty')
