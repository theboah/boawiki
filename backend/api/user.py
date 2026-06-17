import bcrypt
import os
from flask import jsonify, request, current_app
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from models import db
from models.user import UserSignUpSchema, Users, UserLoginSchema, user_exists
from models.whitelist import _is_email_whitelisted

api = Blueprint('user', 'user', url_prefix='/user')


@api.route('/methods', methods=['GET']) 
def methods_available():
    if current_app.config['TESTING']:
        return jsonify({"available": "email"}), 200
    if current_app.config.get('AUTH_URL') is not None or "":
        return jsonify({"available": "oauth2"}), 200
    return jsonify({"available": "none"}), 200

# EMAIL

@api.route('/signup', methods=['POST'])
@api.arguments(UserSignUpSchema,required=True)
def user_sign_up_email():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    if not _is_email_whitelisted(data['email']):
        return jsonify({"error": "Email is not whitelisted"}), 403
    
    if Users.query.filter_by(email=data['email']).first() or Users.query.filter_by(name=data['name']).first():
        return jsonify({"error": "Prohibited action"}), 400
    
    if data['user_type'] not in ['player', 'dm']:
        return jsonify({"error": "Invalid user type"}), 400
    
    
    passtext = data['password']
    hashed_password = bcrypt.hashpw(passtext.encode('utf-8'), bcrypt.gensalt())
    
    new_user = Users(
        name=data['name'],
        email=data['email'],
        user_type=data['user_type'],
        password=hashed_password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


#Need to restrict login route with rate limit for ip
@api.route('/login', methods=['POST'])
@api.arguments(UserLoginSchema,required=True)
def user_login_email():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    if not _is_email_whitelisted(data['email']):
        return jsonify({"error": "Email is not whitelisted"}), 403
    
    user = Users.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "Authentication failed"}), 403
        
    if bcrypt.checkpw(data['password'].encode('utf-8'), user.password):
        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user_id": user.id}), 200
    
    return jsonify({"error": "Authentication failed"}), 403


# OAUTH2


