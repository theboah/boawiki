from flask import Blueprint, jsonify, request 
from models.article import Article
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('api', __name__, url_prefix='/api/v1/article')

@api.route('/create', methods=['POST'])
@jwt_required()
def create_article():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    from models import db
    from models.article import Articles
    
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

@api.route('/move', methods=['POST'])
@jwt_required()
def move_article():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    article_id = data.get('article_id')
    new_parent_id = data.get('parent_article_id')
    
    if not article_id or new_parent_id is None:
        return jsonify({"error": "article_id and parent_article_id are required"}), 400
    
    from models import db
    from models.article import Articles
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
        
    article.parent_article_id = new_parent_id
    db.session.commit()
    
    return jsonify({"message": "Article moved successfully"}), 200

@api.route('/delete', methods=['DELETE'])
@jwt_required()
def delete_article():
    user_id = get_jwt_identity()
    data = request.get_json()
    article_id = data.get('article_id')
    
    if not article_id:
        return jsonify({"error": "article_id is required"}), 400
    
    from models import db
    from models.article import Articles
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
        
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
        
    db.session.delete(article)
    db.session.commit()
    
    return jsonify({"message": "Article deleted"}), 200

@api.route('/get_article_by_id/<int:article_id>', methods=['GET'])
@jwt_required()
def get_article(article_id):
    user_id = get_jwt_identity()
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
        
    from models.article import Articles
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

@api.route('/get_all_articles_for/<int:user_id>', methods=['GET'])
@jwt_required()
def get_articles_for_user(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"error": "Unauthorized"}), 403
        
    from models.article import Articles
    articles = Articles.query.filter_by(author_id=str(user_id)).all()
    
    return jsonify([{
        "id": a.id,
        "title": a.title,
        "content": a.content
    } for a in articles]), 200


#Helper
def user_has_access_to_article(user_id, article_id):
    from models.article import Articles
    article = Articles.query.get(article_id)
    if not article:
        return False
    if article.author_id == str(user_id):
        return True
    if article.permitted_usernames and str(user_id) in article.permitted_usernames:
        return True
    return False

