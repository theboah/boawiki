from flask import jsonify, request 
from flask_smorest import Blueprint
from models import db
from models.link import Links, LinksSchema
from models.user import user_exists
from models.article import user_has_access_to_article
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('link', 'link', url_prefix='/link')

@api.route('/create', methods=['POST'])
@jwt_required()
@api.response(200, LinksSchema)
def create_link():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    
    
    
    data = request.get_json()
    
    from_article_id = data.get('from_article_id')
    to_article_id = data.get('to_article_id')
    to_string = data.get('to_string')
    type_string = data.get('type_string')
    
    if not from_article_id:
        return jsonify({"error": "from_article_id is required"}), 400
    
    if not to_article_id and not to_string:
        return jsonify({"error": "Either to_article_id or to_string is required"}), 400

    if not user_has_access_to_article(user_id, from_article_id):
        return jsonify({"error": "Access denied"}), 403
    
    if to_article_id:
        if not user_has_access_to_article(user_id, to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
    # Unique link ID: from_article_id + to_article_id (or to_string if waiting)
    unique_id = f"{from_article_id}_{to_article_id if to_article_id else to_string}"
    
    existing_link = Links.query.filter_by(unique_link_id=unique_id).first()
    if existing_link:
        return jsonify({"error": "Link already exists"}), 400
        
    new_link = Links(
        unique_link_id=unique_id,
        from_article_id=from_article_id,
        to_article_id=to_article_id,
        to_string=to_string or "",
        type_string=type_string or "default",
        waiting=True if not to_article_id else False
    )
    
    try:
        db.session.add(new_link)
        db.session.commit()
        return jsonify({"message": "Link created", "id": new_link.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api.route('/delete', methods=['POST'])
@jwt_required()
@api.response(200, LinksSchema)
def delete_link():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    link_id = data.get('link_id')
    
    if not link_id:
        return jsonify({"error": "link_id is required"}), 400
    
        
    link = Links.query.get(link_id)
    if not link:
        return jsonify({"error": "Link not found"}), 404
    
    if not user_has_access_to_article(user_id, link.from_article_id):
        return jsonify({"error": "Access denied"}), 403
    
    if link.to_article_id:
        if not user_has_access_to_article(user_id, link.to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
        
    db.session.delete(link)
    db.session.commit()
    
    return jsonify({"message": "Link deleted"}), 200

@api.route('/get_all_links_for/<int:article_id>', methods=['POST'])
@jwt_required()
@api.response(200, LinksSchema)
def get_links_for_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
    
    links = Links.query.filter_by(from_article_id=article_id).all()
    
    permitted_links = []
    
    for link in links:
        if user_has_access_to_article(user_id, link.to_article_id):
            permitted_links.append(link)
    
    return jsonify([{
        "id": l.id,
        "unique_link_id": l.unique_link_id,
        "to_article_id": l.to_article_id,
        "to_string": l.to_string,
        "type_string": l.type_string,
        "waiting": l.waiting
    } for l in permitted_links]), 200
