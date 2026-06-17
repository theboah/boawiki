from flask import jsonify, request
from flask_smorest import Blueprint
from models import db
from models.settings import Settings, SettingsSchema
from models.user import user_exists
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('settings', 'settings', url_prefix='/settings')


#get settings
@api.route('/get', methods=['GET'])
@jwt_required()
@api.response(200, SettingsSchema(only=['background_colour', 'accent_colour', 'font', 'user_colour', 'dark_mode']))
def get_settings():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    
    settings = Settings.query.filter_by(user_id=user_id).first()
    
    if not settings:
        return jsonify({"error": "Settings not found"}), 404
    
    return jsonify(SettingsSchema().dump(settings)), 200

#update settings
@api.route('/update', methods=['POST'])
@jwt_required()
@api.response(200, SettingsSchema(only=['background_colour', 'accent_colour', 'font', 'user_colour', 'dark_mode']))
@api.arguments(SettingsSchema(only=['background_colour', 'accent_colour', 'font', 'user_colour', 'dark_mode']),required=True)
def update_settings():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        # Create default settings if they don't exist
        settings = Settings(user_id=user_id)
    
    settings.background_colour = data.get('background_colour', settings.background_colour)
    settings.accent_colour = data.get('accent_colour', settings.accent_colour)
    settings.font = data.get('font', settings.font)
    settings.user_colour = data.get('user_colour', settings.user_colour)
    settings.dark_mode = data.get('dark_mode', settings.dark_mode)
    
    try:
        db.session.add(settings)
        db.session.commit()
        return jsonify({"message": "Settings updated"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

#reset settings
@api.route('/reset', methods=['POST'])
@api.response(200, SettingsSchema(only=['background_colour', 'accent_colour', 'font', 'user_colour', 'dark_mode']))
@jwt_required()
def reset_settings():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    
    settings = Settings.query.filter_by(user_id=user_id).first()
    if not settings:
        return jsonify({"error": "Settings not found"}), 404
        
    settings.background_colour = None
    settings.accent_colour = None
    settings.font = None
    settings.user_colour = None
    settings.dark_mode = False
    
    try:
        db.session.commit()
        return jsonify({"message": "Settings reset"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400