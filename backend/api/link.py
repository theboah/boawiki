from flask import Blueprint, jsonify, request 
from models.link import link
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('api', __name__, url_prefix='/api/v1/link')


@api.route('/create', methods=['POST'])
@jwt_required()
def create_link():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    from_article_id = data.get('from_article_id')
    to_article_id = data.get('to_article_id')
    to_string = data.get('to_string')
    type_string = data.get('type_string')
    
    if not from_article_id:
        return jsonify({"error": "from_article_id is required"}), 400
    
    if not to_article_id and not to_string:
        return jsonify({"error": "Either to_article_id or to_string is required"}), 400

    from models import db
    from models.link import Links
    
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
def delete_link():
    user_id = get_jwt_identity()
    data = request.get_json()
    link_id = data.get('link_id')
    
    if not link_id:
        return jsonify({"error": "link_id is required"}), 400
        
    from models import db
    from models.link import Links
    
    link = Links.query.get(link_id)
    if not link:
        return jsonify({"error": "Link not found"}), 404
        
    db.session.delete(link)
    db.session.commit()
    
    return jsonify({"message": "Link deleted"}), 200

@api.route('/get_all_links_for/<int:article_id>', methods=['POST'])
@jwt_required()
def get_links_for_article(article_id):
    from models.link import Links
    links = Links.query.filter_by(from_article_id=article_id).all()
    
    return jsonify([{
        "id": l.id,
        "unique_link_id": l.unique_link_id,
        "to_article_id": l.to_article_id,
        "to_string": l.to_string,
        "type_string": l.type_string,
        "waiting": l.waiting
    } for l in links]), 200
