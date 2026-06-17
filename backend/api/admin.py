from flask import jsonify, request
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.models.whitelist import Whitelist, _is_email_whitelisted, WhitelistSchema
from models import db
from models.user import Users, UserSchema, user_exists, _remove_user

api = Blueprint('admin', 'admin', url_prefix='/admin')

@api.route('/whitelist', methods=['POST'])
@jwt_required()
@api.response(200, WhitelistSchema(many=True))
def get_email_whitelist():
    """Get the email whitelist. Only accessible to admin users.
    ---
    """
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not Users.query.get(user_id).admin:
        return jsonify({"error": "Access denied"}), 403
    
    whitelist_entries = Whitelist.email.all()
    schema = WhitelistSchema(many=True)
    return schema.dump(whitelist_entries)

@api.route('/whitelist/add/<email>', methods=['POST'])
@jwt_required()
def add_email_to_whitelist(email):
    """Add an email to the whitelist. Only accessible to admin users.
    ---
    """
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not Users.query.get(user_id).admin:
        return jsonify({"error": "Access denied"}), 403
    
    if _is_email_whitelisted(email):
        return jsonify({"error": "Email already whitelisted"}), 400
    
    new_entry = Whitelist(email=email)

    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Email added to whitelist"}), 201

@api.route('/whitelist/delete/<email>', methods=['POST'])
@jwt_required()
def remove_email_from_whitelist(email):
    """Remove an email from the whitelist. This does not remove the associated account with the email in the whitelist. Only accessible to admin users.
    ---
    """
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    if not Users.query.get(user_id).admin:
        return jsonify({"error": "Access denied"}), 403

    whitelist_entry = Whitelist.query.get(email)
    if not whitelist_entry:
        return jsonify({"error": "Email not found in whitelist"}), 404

    db.session.delete(whitelist_entry)
    db.session.commit()
    return jsonify({"message": "Email removed from whitelist"}), 200

#Users

@api.route('/users', methods=['GET'])
@jwt_required()
@api.response(200, UserSchema(only=('id', 'name', 'email', 'user_type'), many=True))
def get_all_users():
    """Get all users. Only accessible to admin users.
    ---
    """
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not Users.query.get(user_id).admin:
        return jsonify({"error": "Access denied"}), 403
    
    users = Users.query.all()
    schema = UserSchema(only=('id', 'name', 'email', 'user_type'), many=True)
    return schema.dump(users)

@api.route('/users/delete/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Remove a user. Only accessible to admin users.
    ---
    """
    admin_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    if not Users.query.get(admin_id).admin:
        return jsonify({"error": "Access denied"}), 403

    user = Users.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    _remove_user(user_id, admin_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200



