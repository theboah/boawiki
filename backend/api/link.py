from flask import jsonify, request 
from flask_smorest import Blueprint
from models import db
from models.link import LinkDataSchema, LinkToUpdateSchema, Links, LinksSchema, get_unique_link_id
from models.user import user_exists
from models.article import user_has_access_to_article
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('link', 'link', url_prefix='/link')

@api.route('/create', methods=['POST'])
@jwt_required()
@api.arguments(LinkDataSchema, required=True)
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
        return jsonify({"message": "Link created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api.route('/delete', methods=['DELETE'])
@jwt_required()
@api.arguments(LinkDataSchema)
def delete_link():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    from_article_id = data.get('from_article_id')
    
    if not from_article_id:
        return jsonify({"error": "from_article_id is required"}), 400
    
    if not user_has_access_to_article(user_id, link.from_article_id):
        return jsonify({"error": "Access denied"}), 403
    
    to_article_id = data.get('to_article_id')
    to_string = data.get('to_string')
    type_string = data.get('type_string')
    if not to_article_id and not to_string:
        return jsonify({"error": "Either to_article_id or to_string is required"}), 400
    
    if link.to_article_id:
        if not user_has_access_to_article(user_id, link.to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
    link = Links.query.get(get_unique_link_id(from_article_id, to_article_id, to_string))
    if not link:
        return jsonify({"error": "Link not found"}), 404
    
    if to_string:
        if link.waiting == False:
            return jsonify({"error": "Incorrect link state provided"}), 400

    db.session.delete(link)
    db.session.commit()
    
    return jsonify({"message": "Link deleted"}), 200

@api.route('/get', methods=['GET'])
@jwt_required()
@api.arguments(LinkDataSchema)
def get_link_id():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    from_article_id = data.get('from_article_id')
    
    if not from_article_id:
        return jsonify({"error": "from_article_id is required"}), 400
    
    if not user_has_access_to_article(user_id, link.from_article_id):
        return jsonify({"error": "Access denied"}), 403
    
    to_article_id = data.get('to_article_id')
    to_string = data.get('to_string')
    type_string = data.get('type_string')
    if not to_article_id and not to_string:
        return jsonify({"error": "Either to_article_id or to_string is required"}), 400
    
    if link.to_article_id:
        if not user_has_access_to_article(user_id, link.to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
    link = Links.query.get(get_unique_link_id(from_article_id, to_article_id, to_string))
    if not link:
        return jsonify({"error": "Link not found"}), 404
    
    if to_string:
        if link.waiting == False:
            return jsonify({"error": "Incorrect link state provided"}), 400
        
    return jsonify(LinksSchema(only=('unique_link_id')).dump(link)), 200

@api.route('/update/<string:link_id>', methods=['PUT'])
@jwt_required()
@api.arguments(LinkToUpdateSchema, required=True)
def update_link_state(link_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    link = Links.query.get(link_id)
    if not link:
        return jsonify({"error": "Link not found"}), 404
    
    if not user_has_access_to_article(user_id, link.from_article_id):
        return jsonify({"error": "Access denied"}), 403
    
    
    if link.to_article_id:
        if not user_has_access_to_article(user_id, link.to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
    to_article_id = data.get('to_article_id')
    if to_article_id:
        if not user_has_access_to_article(user_id, to_article_id):
            return jsonify({"error": "Access denied"}), 403
    
    to_string = data.get('to_string')
    type_string = data.get('type_string')
    
    if to_article_id and to_string:
        return jsonify({"error": "Cannot provide both to_article_id and to_string"}), 400
    
    if type_string:
        link.type_string = type_string
    
    if to_string:
        link.waiting = True
        link.to_string = to_string
    
    if to_article_id:
        link.waiting = False
        link.to_string = None
        link.to_article_id = to_article_id
    
    db.session.commit()
    
    return jsonify({"message": "Link updated"}), 200

@api.route('/get_all_links_for/<int:article_id>', methods=['GET'])
@jwt_required()
@api.response(200, LinksSchema(many=True))
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
        "unique_link_id": l.unique_link_id,
        "to_article_id": l.to_article_id,
        "to_string": l.to_string,
        "type_string": l.type_string,
        "waiting": l.waiting
    } for l in permitted_links]), 200
