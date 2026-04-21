import os

class Config:
    # Si DATABASE_URL existe (Render), on l'utilise. Sinon, on garde le local.
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://neondb_owner:npg_epmB3rX6KuaD@ep-empty-mountain-a4sjb3xc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    # Note : Render donne souvent une URL commençant par postgres://
    # SQLAlchemy requiert parfois postgresql:// (avec le 'ql')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'une-cle-par-defaut-tres-longue')
