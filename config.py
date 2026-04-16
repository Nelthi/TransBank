import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:azerty@localhost:5432/banquebd'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'ta_cle_secrete_ultra_securisee'
