import os

class Config:
    # 1. On essaie de récupérer la variable d'environnement de Render
    # 2. Si elle n'existe pas, on met l'URL locale par défaut pour ne pas crash
    uri = os.environ.get('postgresql://neondb_owner:npg_a7ouKbvihM5R@ep-wandering-glade-an3i6xql-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
    
    if uri:
        # Render utilise souvent 'postgres://', mais SQLAlchemy exige 'postgresql://'
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
    else:
        # URL de secours pour le développement local si DATABASE_URL est vide
        uri = 'postgresql://postgres:azerty@localhost:5432/banquebd'
    
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ma-cle-tres-secrete-123')
