from marshmallow import Schema, fields

from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
class Users(db.Model):
    __tablename__ = "users"

    id: db.Column = db.Column(db.Integer, primary_key=True)
    name: db.Column = db.Column(db.String(255), nullable=False)
    avatar_image: db.Column = db.Column(db.String(255))
    email: db.Column = db.Column(db.String(255), unique=True)
    user_type: db.Column = db.Column(db.String(255))
    auth_provider: db.Column = db.Column(db.String(255))
    admin: db.Column = db.Column(db.Boolean, default=False)
    password: db.Column = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"id={self.id!r}, name={self.name!r})"
    
def user_exists(user_id) -> bool:
    user = Users.query.get(user_id)
    if user:
        return True
    return False

#helper to remove user from articles and settings when deleted
def _remove_user(remove_user_id, admin_user_id):
    from models.article import Articles
    from models.settings import Settings
    #We want to go to each article that had author as the user and then set it to the admin
    authored_articles = Articles.query.filter_by(author_id=remove_user_id).all()
    for article in authored_articles:
        article.author_id = admin_user_id
    
    #We want to go and remove the user id from the article permissions for all articles that have the user id in the permitted ids
    permitted_articles = Articles.query.filter(Articles.permitted_user_ids.contains(str(remove_user_id))).all()
    for article in permitted_articles:
        permitted_ids = article.permitted_user_ids.split(',')
        if str(remove_user_id) in permitted_ids:
            permitted_ids.remove(str(remove_user_id))
            article.permitted_user_ids = ','.join(permitted_ids)
    
    
    #we want to remove the settings for the user and any associated images etc from file storage
    settings = Settings.query.filter_by(user_id=remove_user_id).first()
    settings_removed = False
    if settings:
        db.session.delete(settings)
        settings_removed = True
        
    db.session.commit()
    
    return {'num_articles':len(authored_articles), 'num_permitted_articles': len(permitted_articles), 'settings_removed': settings_removed}

class UserLoginSchema(Schema):
    email = fields.Str()
    password = fields.Str()

class UserSignUpSchema(Schema):
    email = fields.Str()
    password = fields.Str()
    user_type = fields.Str()
class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True