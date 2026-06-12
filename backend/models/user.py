from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
class Users(db.Model):
    __tablename__ = "users"

    id: db.Column = db.Column(db.Integer, primary_key=True)
    name: db.Column = db.Column(db.String(255), nullable=False)
    avatar_image: db.Column = db.Column(db.String(255))
    email: db.Column = db.Column(db.String(255), unique=True)
    auth_token: db.Column = db.Column(db.String(255), unique=True)
    user_type: db.Column = db.Column(db.String(255))
    auth_provider: db.Column = db.Column(db.String(255))

    def __repr__(self) -> str:
        return f"id={self.id!r}, name={self.name!r})"
    
def user_exists(user_id) -> bool:
    user = Users.query.get(user_id)
    if user:
        return True
    return False

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True