from datetime import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, ENUM

db = SQLAlchemy()

# Définition de l'énumération pour les transactions
transaction_type_enum = ENUM('TRANSFER', 'DEPOSIT', 'WITHDRAWAL', name='transaction_type')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    accounts = db.relationship('Account', backref='owner', lazy=True)
    auth_methods = db.relationship('AuthMethod', backref='user', lazy=True)

class AuthMethod(db.Model):
    __tablename__ = 'auth_methods'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    
    # Stratégie pour Login/Password
    login = db.Column(db.String(50), unique=True)
    hashed_password = db.Column(db.String(255))
    
    # Stratégie pour Reconnaissance Faciale
    # On stocke le vecteur facial sous forme de texte ou JSON
    face_template = db.Column(db.Text) 
    precision_threshold = db.Column(db.Numeric(3, 2), default=0.90)
    
    auth_type = db.Column(db.String(20), nullable=False) # 'PASSWORD' ou 'FACIAL'

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.BigInteger, primary_key=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    # Utilisation de Numeric pour la précision bancaire
    balance = db.Column(db.Numeric(19, 2), default=0.00)
    currency = db.Column(db.String(3), default='XAF') # Franc CFA par exemple
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Contrainte : le solde ne doit pas être négatif (pour le MVP)
    __table_args__ = (
        db.CheckConstraint('balance >= 0', name='check_balance_positive'),
    )

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.BigInteger, primary_key=True)
    reference = db.Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    amount = db.Column(db.Numeric(19, 2), nullable=False)
    t_type = db.Column(transaction_type_enum, nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    source_account_id = db.Column(db.BigInteger, db.ForeignKey('accounts.id'))
    destination_account_id = db.Column(db.BigInteger, db.ForeignKey('accounts.id'))
