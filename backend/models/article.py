from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields

class Articles(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(255), nullable=False, unique=True)
    content = db.Column(db.String(255))
    permitted_usernames = db.Column(db.ARRAY(db.String(255)))
    parent_article_id = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=True, unique=False)
    children = db.relationship("Articles", backref=db.backref("parent", remote_side=[id]))
    icon = db.Column(db.String(255))
    colour = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"id={self.id!r}, title={self.title!r}, content={self.content!r})"
    
    def to_dict(self):
        return {
            "id": self.id,
            "author_id": self.author_id,
            "title": self.title,
            "content": self.content,
            "permitted_usernames": self.permitted_usernames,
            "parent_article_id": self.parent_article_id,
            "icon": self.icon,
            "colour": self.colour
        }
        
def user_has_access_to_article(user_id, article_id):
    article = Articles.query.get(article_id)
    if not article:
        return False
    if article.author_id == user_id:
        return True
    if article.permitted_usernames and user_id in article.permitted_usernames:
        return True
    return False

class ArticleCreateSchema(Schema):
    """Schema for creating a new article"""
    title = fields.Str()
    content = fields.Str()
    parent_article_id = fields.Int()

class ArticleMoveSchema(Schema):
    """Schema for moving an article to a new parent"""
    parent_article_id = fields.Int()

class ArticleResponseSchema(Schema):
    """Schema for returning public article details"""
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    author_id = fields.Int()
    parent_article_id = fields.Int()

class ArticlePermissionRequestSchema(Schema):
    article_id = fields.Int()
    user_id = fields.Int()


class ArticlesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Articles
        load_instance = True
        include_fk = True
        include_relationships = True
