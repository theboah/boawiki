from flask import jsonify, request
from flask_smorest import Blueprint
from models import db
from models.article import Articles, ArticlesSchema, user_has_access_to_article
from models.user import user_exists
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('article', 'article', url_prefix='/article')

@api.route('/create/', methods=['POST'])
@jwt_required()
@api.response(200, ArticlesSchema)
def create_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_article = Articles(
        title=data['title'],
        content=data.get('content', ''),
        author_id=user_id,
        folder_id=data.get('folder_id'),
        parent_article_id=data.get('parent_article_id')
    )
    
    try:
        db.session.add(new_article)
        db.session.commit()
        return jsonify({"message": "Article created", "id": new_article.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@api.route('/move/<int:article_id>', methods=['PUT'])
@jwt_required()
@api.response(200, ArticlesSchema)
def move_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    article_id = data.get('article_id')
    new_parent_id = data.get('parent_article_id')
    
    if not article_id or new_parent_id is None:
        return jsonify({"error": "article_id and parent_article_id are required"}), 400
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
        
    article.parent_article_id = new_parent_id
    db.session.commit()
    
    return jsonify({"message": "Article moved successfully"}), 200

@api.route('/delete/<int:article_id>', methods=['DELETE'])
@jwt_required()
@api.response(200, ArticlesSchema)
def delete_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    article_id = data.get('article_id')
    
    if not article_id:
        return jsonify({"error": "article_id is required"}), 400
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
        
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
        
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({"message": "Article deleted"}), 200

@api.route('/get_article_by_id/<int:article_id>/', methods=['GET'])
@jwt_required()
@api.response(200, ArticlesSchema)
def get_article(article_id):
    user_id = get_jwt_identity()
    
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
        
    return jsonify({
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "author_id": article.author_id,
        "parent_article_id": article.parent_article_id
    }), 200

@api.route('/get_all_articles_for/<int:user_id>/', methods=['GET'])
@jwt_required()
@api.response(200, ArticlesSchema)
def get_articles_for_user(user_id):
    current_user = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if current_user != user_id:
        return jsonify({"error": "Unauthorized"}), 403
        
    articles += Articles.query.filter(Articles.author_id == str(user_id) or Articles.permitted_usernames.contains(str(user_id))).all()
    
    json = jsonify([a.to_dict() for a in articles])
    return json, 200

@api.route('/permission/add/<int:article_id>', methods=['PUT'])
@jwt_required()
@api.response(200, ArticlesSchema)
def permit_user_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403

    user_to_change = request.args.get('user_id')
    if not user_to_change:
        return jsonify({"error": "user_id query parameter is required"}), 400
    
    if not user_exists(user_to_change):
        return jsonify({"error": "User to change not found"}), 404
    
    if user_has_access_to_article(user_to_change, article_id):
        return jsonify({"error": "User to change already has access to this article"}), 400
    
    article.permitted_usernames.append(str(user_to_change))

    db.session.commit()
    return jsonify({"message": "Article updated successfully"}), 200

@api.route('/permission/remove/<int:article_id>', methods=['PUT'])
@jwt_required()
@api.response(200, ArticlesSchema)
def remove_user_permission(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404

    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404

    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
    
    user_to_change = request.args.get('user_id')
    if not user_to_change:
        return jsonify({"error": "user_id query parameter is required"}), 400
    
    if not user_exists(user_to_change):
        return jsonify({"error": "User to change not found"}), 404
    
    if not user_has_access_to_article(user_to_change, article_id):
        return jsonify({"error": "User to change does not have access to this article"}), 400

    usernames = []
    for username in article.permitted_usernames:
        if username != user_to_change:
            usernames.append(username)
            
    article.permitted_usernames = usernames
    db.session.commit()
    return jsonify({"message": "Article updated successfully"}), 200

#Helpers






