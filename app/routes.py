from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from app.models import User

auth_bp = Blueprint('auth', __name__)

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

    