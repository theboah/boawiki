from flask import Blueprint, jsonify, request 
from models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('api', __name__, url_prefix='/api/v1/user')


@api.route('/create', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({"error": "Name and email are required"}), 400
    
    from models import db
    from models.user import Users
    
    # Check if user already exists
    if Users.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists"}), 400
        
    new_user = Users(
        name=data['name'],
        email=data['email'],
        avatar_image=data.get('avatar_image'),
        user_type=data.get('user_type', 'user'),
        auth_provider=data.get('auth_provider', 'local')
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Create default settings for the new user
        from models.settings import Settings
        default_settings = Settings(user_id=new_user.id)
        db.session.add(default_settings)
        db.session.commit()
        
        return jsonify({"message": "User created", "id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api.route('/delete', methods=['POST'])
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    
    from models import db
    from models.user import Users
    
    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "User deleted"}), 200