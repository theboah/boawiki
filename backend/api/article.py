from flask import jsonify, request
from flask_smorest import Blueprint
from models import db
from models.article import Articles, ArticlesSchema, ArticlePermissionRequestSchema, ArticleCreateSchema, ArticleMoveSchema, ArticleResponseSchema, user_has_access_to_article
from models.user import user_exists
from flask_jwt_extended import jwt_required, get_jwt_identity
api = Blueprint('article', 'article', url_prefix='/article')

@api.route('/create/', methods=['POST'])
@jwt_required()
@api.arguments(ArticleCreateSchema(), required=True)
def create_article():
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    title = data['title']
    if title == "":
        return jsonify({"error": "Title cannot be empty"}), 400
    if Articles.query.filter_by(title=title).first():
        return jsonify({"error": "Article with this title already exists"}), 400
    if len(title) > 255:
        return jsonify({"error": "Title cannot be longer than 255 characters"}), 400
    
    parent_article_id = data.get('parent_article_id')
    if parent_article_id:
        if not user_has_access_to_article(user_id, parent_article_id):
            return jsonify({"error": "Access denied"}), 403
        
        if not Articles.query.get(parent_article_id):
            return jsonify({"error": "Parent article not found"}), 404
    
    if not parent_article_id:
        parent_article_id = None    
    
    new_article = Articles(
        title=title,
        content=data.get('content', ''),
        author_id=user_id,
        parent_article_id=parent_article_id
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
@api.arguments(ArticleMoveSchema(), required=True)
def move_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
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
def delete_article(article_id):
    user_id = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
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
@api.response(200, ArticleResponseSchema())
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

@api.route('/update/<int:article_id>/', methods=['PUT'])
@jwt_required()
def update_article(article_id):
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if not user_has_access_to_article(user_id, article_id):
        return jsonify({"error": "Access denied"}), 403
    
    article = Articles.query.get(article_id)
    if not article:
        return jsonify({"error": "Article not found"}), 404
    
    #validate colour code has 6 rrggbb charecters with leading #
    colour = data.get('colour')
    if colour:
        if colour[0] != '#' or len(colour) != 7:
            return jsonify({"error": "Invalid colour code"}), 400
        if not all(c in '0123456789abcdefABCDEF' for c in colour[1:]):
            return jsonify({"error": "Invalid colour code"}), 400
        article.colour = colour
    
    #TODO: Validate Icon content
    
    title= data.get('title')
    if title:
        if title == "":
            return jsonify({"error": "Title cannot be empty"}), 400
        if Articles.query.filter(Articles.title == title, Articles.id != article_id).first():
            return jsonify({"error": "Article with this title already exists"}), 400
        if len(title) > 255:
            return jsonify({"error": "Title cannot be longer than 255 characters"}), 400
        article.title = title
    
    db.session.commit()
    
        
    return jsonify({"message": "Article updated successfully"}), 200

@api.route('/get_all_articles_for/<int:user_id>/', methods=['GET'])
@jwt_required()
@api.response(200, ArticleResponseSchema(many=True))
def get_articles_for_user(user_id):
    current_user = get_jwt_identity()
    if not user_exists(user_id):
        return jsonify({"error": "User not found"}), 404
    
    if current_user != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    articles = []
    articles += Articles.query.filter(Articles.author_id == str(user_id) | Articles.permitted_usernames.contains(str(user_id))).all()
    
    json = jsonify([a.to_dict() for a in articles])
    return json, 200

@api.route('/permission/add/<int:article_id>', methods=['PUT'])
@jwt_required()
@api.arguments(ArticlePermissionRequestSchema,required=True)
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
    new_permissions = article.permitted_usernames
    new_permissions.append(str(user_to_change))
    article.permitted_usernames = new_permissions

    db.session.commit()
    return jsonify({"message": "Article updated successfully"}), 200

@api.route('/permission/remove/<int:article_id>', methods=['PUT'])
@jwt_required()
@api.arguments(ArticlePermissionRequestSchema,required=True)
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






