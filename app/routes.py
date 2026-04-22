from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.models import User
import random
import string
from app.models import Account, Transaction
from app.models import db

auth_bp = Blueprint('auth', __name__)


## fonction de décoration administrateur


from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # On suppose que l'ID de la personne qui fait la requête est envoyé 
        # dans un header 'X-Admin-ID'
        admin_id = request.headers.get('X-Admin-ID')
        
        if not admin_id:
            return jsonify({"error": "Identification admin manquante"}), 401
            
        admin_user = User.query.get(admin_id)
        
        if not admin_user or not admin_user.is_admin:
            return jsonify({"error": "Accès refusé : vous n'êtes pas administrateur"}), 403
            
        return f(*args, **kwargs)
    return decorated_function










# Route pour l'inscription d'un nouvel utilisateur


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Création d'un nouvel utilisateur avec compte bancaire
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: RegisterData
          required:
            - first_name
            - last_name
            - email
            - login
            - password
          properties:
            first_name:
              type: string
              example: Nelson
            last_name:
              type: string
              example: Neylcy
            email:
              type: string
              example: toure@test.com
            login:
              type: string
              example: neylcy237
            password:
              type: string
              example: MonSuperPassword123
    responses:
      201:
        description: "Utilisateur créé avec succès et compte bancaire initialisé"
      400:
        description: "Champs manquants ou données invalides"
      500:
        description: "Erreur serveur (ex: email déjà utilisé)"
    """
    data = request.get_json()
    
    # Vérification basique des champs requis
    required = ['first_name', 'last_name', 'email', 'login', 'password']
    if not all(k in data for k in required):
        return jsonify({"error": "Champs manquants"}), 400

    try:
        user = UserService.create_user_with_password(
            data['first_name'], 
            data['last_name'], 
            data['email'], 
            data['login'], 
            data['password']
        )
        return jsonify({
            "message": "Utilisateur créé avec succès",
            "user_id": user.id,
            "email": user.email
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    





# Route pour afficher tous les utilisateurs (pour test ou admin)

@auth_bp.route('/users', methods=['GET'])
def get_all_users():
    """
    Récupérer la liste de tous les utilisateurs inscrits
    ---
    responses:
      200:
        description: Liste des utilisateurs retournée avec succès
        schema:
          properties:
            users:
              type: array
              items:
                properties:
                  id:
                    type: integer
                  first_name:
                    type: string
                  last_name:
                    type: string
                  email:
                    type: string
                  created_at:
                    type: string
      500:
        description: "Erreur lors de la récupération des données"
    """
    
    try:
        # Récupérer tous les utilisateurs de la base de données
        users = User.query.all()
        
        # Transformer la liste d'objets en format JSON
        output = []
        for user in users:
            user_data = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            output.append(user_data)
        
        return jsonify({"users": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


from werkzeug.security import check_password_hash
from app.models import AuthMethod, Account



#route pour modifier un utilisateur etant administrateur

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required  # <-- Le verrou est ici
def update_user(user_id):
    """
    Modifier un utilisateur (ADMIN UNIQUEMENT)
    ---
    parameters:
      - name: X-Admin-ID
        in: header
        type: integer
        required: true
        description: Doit être 'admin'
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          id: UpdateData
          properties:
            first_name: {type: string}
            last_name: {type: string}
            email: {type: string}
    responses:
      200: {description: "Succès"}
      403: {description: "Interdit"}
      404: {description: "Non trouvé"}
    """
    data = request.get_json()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    try:
        if 'first_name' in data: user.first_name = data['first_name']
        if 'last_name' in data: user.last_name = data['last_name']
        if 'email' in data:
            user.email = data['email']

        db.session.commit()
        return jsonify({"message": "Utilisateur mis à jour par l'admin"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500






#route pour supprimer un utilisateur etant administrateur

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """
    Supprimer un utilisateur (ADMIN UNIQUEMENT)
    ---
    parameters:
      - name: X-Admin-ID
        in: header
        type: integer
        required: true
        description: ID de l'administrateur effectuant l'action
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID de l'utilisateur à supprimer
    responses:
      200:
        description: "Utilisateur supprimé avec succès"
      403:
        description: "Accès refusé"
      404:
        description: "Utilisateur non trouvé"
      500:
        description: "Erreur lors de la suppression"
    """
    # 1. Rechercher l'utilisateur à supprimer
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    try:
        # Optionnel : Empêcher un admin de se supprimer lui-même par erreur
        admin_id = int(request.headers.get('X-Admin-ID'))
        if admin_id == user_id:
            return jsonify({"error": "Un administrateur ne peut pas supprimer son propre compte via cette route"}), 400

        # 2. Supprimer l'utilisateur de la session
        db.session.delete(user)
        
        # 3. Valider la transaction en base de données
        db.session.commit()

        return jsonify({
            "message": f"L'utilisateur {user.first_name} {user.last_name} a été supprimé avec succès"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500




#  Route pour la connexion d'un utilisateur avec login et mot de passe


@auth_bp.route('/login', methods=['POST'])

def login():
    """
    Connexion utilisateur par mot de passe
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: LoginData
          required:
            - login
            - password
          properties:
            login:
              type: string
              example: neylcy237
            password:
              type: string
              example: MonSuperPassword123
    responses:
      200:
        description: "Connexion réussie"
      401:
        description: "Identifiants invalides"
    """
    data = request.get_json()
    
    login_input = data.get('login')
    password_input = data.get('password')

    if not login_input or not password_input:
        return jsonify({"error": "Login et mot de passe requis"}), 400

    # 1. Chercher la méthode d'authentification par le login
    auth = AuthMethod.query.filter_by(login=login_input, auth_type='PASSWORD').first()

    # 2. Vérifier si l'utilisateur existe et si le mot de passe est correct
    if auth and check_password_hash(auth.hashed_password, password_input):
        user = auth.user
        
        # 3. Récupérer le compte principal pour l'afficher au login (optionnel mais utile)
        account = Account.query.filter_by(user_id=user.id).first()
        
        return jsonify({
            "message": "Connexion réussie",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            },
            "account": {
                "number": account.account_number if account else "N/A",
                "balance": float(account.balance) if account else 0.0
            }
        }), 200
    else:
        # Erreur générique pour ne pas aider un hacker à deviner si le login existe
        return jsonify({"error": "Identifiants invalides"}), 401

    


# Route pour créer un compte bancaire pour un utilisateur existant
 

@auth_bp.route('/accounts', methods=['POST'])
def create_account():
    """
    Créer un compte bancaire pour un utilisateur
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            user_id:
              type: integer
              example: 1
            initial_balance:
              type: number
              example: 5000.0
            currency:
              type: string
              example: XAF
    responses:
      201:
        description: Compte créé avec succès
      404:
        description: Utilisateur non trouvé
    """
    data = request.get_json()
    user_id = data.get('user_id')
    
    # 1. Vérifier que l'utilisateur existe
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    try:
        # 2. Générer un numéro de compte unique (ex: TRB123456789)
        random_digits = ''.join(random.choices(string.digits, k=9))
        account_number = f"TRB{random_digits}"

        # 3. Créer l'objet Account selon ton modèle
        new_account = Account(
            account_number=account_number,
            balance=data.get('initial_balance', 0.00),
            currency=data.get('currency', 'XAF'),
            user_id=user.id
        )

        db.session.add(new_account)
        db.session.commit()

        return jsonify({
            "message": "Compte bancaire créé",
            "account": {
                "id": new_account.id,
                "account_number": new_account.account_number,
                "balance": str(new_account.balance),
                "currency": new_account.currency
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    



# Route pour récupérer les comptes d'un utilisateur


@auth_bp.route('/users/<int:user_id>/accounts', methods=['GET'])
def get_user_accounts(user_id):
    """
    Récupérer tous les comptes bancaires d'un utilisateur spécifique
    ---
    tags:
      - Accounts
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID de l'utilisateur dont on veut lister les comptes
    responses:
      200:
        description: Liste des comptes récupérée avec succès
        schema:
          properties:
            user:
              type: string
              example: "Nelson"
            accounts:
              type: array
              items:
                properties:
                  account_number:
                    type: string
                    example: "TRB123456789"
                  balance:
                    type: number
                    example: 50000.0
                  currency:
                    type: string
                    example: "XAF"
                  created_at:
                    type: string
                    format: date-time
      404:
        description: Utilisateur non trouvé
      500:
        description: Erreur serveur
    """
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Utilisateur non trouvé"}), 404
            
        accounts = []
        for acc in user.accounts:
            accounts.append({
                "account_number": acc.account_number,
                "balance": float(acc.balance),
                "currency": acc.currency,
                "created_at": acc.created_at.strftime('%Y-%m-%d %H:%M:%S') if acc.created_at else None
            })
            
        return jsonify({
            "user": user.first_name, 
            "accounts": accounts
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




# Route pour effectuer un virement entre deux comptes bancaires



    from app.models import db, User, Account, Transaction
from decimal import Decimal

@auth_bp.route('/transactions/transfer', methods=['POST'])
def transfer_money():
    """
    Effectuer un virement entre deux comptes
    ---
    tags:
      - Transactions
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            source_account_number:
              type: string
              example: "TRB123456789"
            destination_account_number:
              type: string
              example: "TRB987654321"
            amount:
              type: number
              example: 1000.0
            description:
              type: string
              example: "Remboursement déjeuner"
    responses:
      200:
        description: Virement effectué avec succès
      400:
        description: Solde insuffisant ou données invalides
      404:
        description: Un des comptes n'existe pas
    """
    data = request.get_json()
    amount = Decimal(str(data.get('amount', 0)))
    source_no = data.get('source_account_number')
    dest_no = data.get('destination_account_number')

    if amount <= 0:
        return jsonify({"error": "Le montant doit être supérieur à zéro"}), 400

    # 1. Récupérer les deux comptes
    source_account = Account.query.filter_by(account_number=source_no).first()
    dest_account = Account.query.filter_by(account_number=dest_no).first()

    if not source_account or not dest_account:
        return jsonify({"error": "Compte source ou destination introuvable"}), 404

    if source_account.id == dest_account.id:
        return jsonify({"error": "Impossible d'effectuer un virement sur le même compte"}), 400

    try:
        # 2. Vérifier le solde
        if source_account.balance < amount:
            return jsonify({"error": "Solde insuffisant"}), 400

        # 3. Opération atomique (Débit / Crédit)
        source_account.balance -= amount
        dest_account.balance += amount

        # 4. Enregistrer la trace dans la table Transactions
        new_tx = Transaction(
            amount=amount,
            t_type='TRANSFER',
            description=data.get('description'),
            source_account_id=source_account.id,
            destination_account_id=dest_account.id
        )

        db.session.add(new_tx)
        
        # 5. Valider définitivement en base de données
        db.session.commit()

        return jsonify({
            "message": "Transfert réussi",
            "reference": str(new_tx.reference),
            "new_balance": float(source_account.balance)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erreur lors de la transaction", "details": str(e)}), 500
    





# Route pour effectuer un dépôt d'argent sur un compte bancaire


from app.models import db, User, Account, Transaction
from decimal import Decimal

@auth_bp.route('/transactions/deposit', methods=['POST'])
def deposit_money():
    """
    Effectuer un dépôt d'argent sur un compte
    ---
    tags:
      - Transactions
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            account_number:
              type: string
              example: "TRB123456789"
            amount:
              type: number
              example: 5000.0
            description:
              type: string
              example: "Dépôt en espèces guichet"
    responses:
      200:
        description: Dépôt réussi
      400:
        description: Montant invalide
      404:
        description: Compte introuvable
    """
    data = request.get_json()
    amount_raw = data.get('amount')
    account_no = data.get('account_number')

    # 1. Validations de base
    if not amount_raw or float(amount_raw) <= 0:
        return jsonify({"error": "Le montant doit être supérieur à zéro"}), 400

    amount = Decimal(str(amount_raw))
    
    # 2. Récupérer le compte
    account = Account.query.filter_by(account_number=account_no).first()
    if not account:
        return jsonify({"error": "Compte introuvable"}), 404

    try:
        # 3. Mise à jour du solde
        account.balance += amount

        # 4. Enregistrement de la transaction
        new_tx = Transaction(
            amount=amount,
            t_type='DEPOSIT',  # Assure-toi que 'DEPOSIT' est dans ton ENUM dans models.py
            description=data.get('description', 'Dépôt d\'argent'),
            destination_account_id=account.id, # Le compte reçoit l'argent
            source_account_id=None # Pas de source pour un dépôt externe
        )

        db.session.add(new_tx)
        db.session.commit()

        return jsonify({
            "message": "Dépôt effectué avec succès",
            "reference": str(new_tx.reference),
            "new_balance": float(account.balance),
            "currency": account.currency
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erreur lors du dépôt", "details": str(e)}), 500
    





# Route pour effectuer un retrait d'argent d'un compte bancaire


@auth_bp.route('/transactions/withdraw', methods=['POST'])
def withdraw_money():
    """
    Effectuer un retrait d'argent d'un compte
    ---
    tags:
      - Transactions
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            account_number:
              type: string
              example: "TRB123456789"
            amount:
              type: number
              example: 2000.0
            description:
              type: string
              example: "Retrait au distributeur automatique"
    responses:
      200:
        description: Retrait réussi
      400:
        description: Solde insuffisant ou montant invalide
      404:
        description: Compte introuvable
    """
    data = request.get_json()
    amount_raw = data.get('amount')
    account_no = data.get('account_number')

    # 1. Validation du montant
    if not amount_raw or float(amount_raw) <= 0:
        return jsonify({"error": "Le montant doit être supérieur à zéro"}), 400

    amount = Decimal(str(amount_raw))
    
    # 2. Récupérer le compte
    account = Account.query.filter_by(account_number=account_no).first()
    if not account:
        return jsonify({"error": "Compte introuvable"}), 404

    try:
        # 3. Vérification du solde disponible
        if account.balance < amount:
            return jsonify({"error": "Solde insuffisant pour effectuer ce retrait"}), 400

        # 4. Mise à jour du solde (Débit)
        account.balance -= amount

        # 5. Enregistrement de la transaction
        new_tx = Transaction(
            amount=amount,
            t_type='WITHDRAWAL', # Vérifie que 'WITHDRAWAL' est dans ton ENUM models.py
            description=data.get('description', 'Retrait d\'argent'),
            source_account_id=account.id, # L'argent sort de ce compte
            destination_account_id=None # Pas de compte de destination interne
        )

        db.session.add(new_tx)
        db.session.commit()

        return jsonify({
            "message": "Retrait effectué avec succès",
            "reference": str(new_tx.reference),
            "remaining_balance": float(account.balance)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Erreur lors du retrait", "details": str(e)}), 500