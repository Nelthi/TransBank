from app.models import db, User, AuthMethod, Account
from werkzeug.security import generate_password_hash
import random
import string

class UserService:
    @staticmethod
    def create_user_with_password(first_name, last_name, email, login, password):
        try:
            # 1. Créer l'utilisateur
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            db.session.add(new_user)
            db.session.flush()  # Pour récupérer l'ID de l'utilisateur avant le commit final

            # 2. Hacher le mot de passe et créer la méthode d'auth
            hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
            auth = AuthMethod(
                user_id=new_user.id,
                auth_type='PASSWORD',
                login=login,
                hashed_password=hashed_pw
            )
            db.session.add(auth)

            # 3. Créer un compte bancaire par défaut pour le MVP
            # Génération d'un numéro de compte aléatoire simple
            acc_number = ''.join(random.choices(string.digits, k=10))
            new_account = Account(
                account_number=f"ACC-{acc_number}",
                balance=0.00,
                user_id=new_user.id
            )
            db.session.add(new_account)

            db.session.commit()
            return new_user
        except Exception as e:
            db.session.rollback()
            raise e