import os

class Config:
    # On cherche la variable d'environnement nommée 'DATABASE_URL' (configurée sur Render)
    # Si elle n'existe pas, on met l'URL de Neon par défaut.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_epmB3rX6KuaD@ep-empty-mountain-a4sjb3xc-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require')
    
    # Correction cruciale si Render utilise postgres:// au lieu de postgresql://
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'azerty')
