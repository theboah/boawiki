from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
class Settings(db.Model):
    __tablename__ = "settings"
    
    user_id: db.Column = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,primary_key=True,)
    background_colour: db.Column = db.Column(db.String(255))
    accent_colour: db.Column = db.Column(db.String(255))
    font: db.Column = db.Column(db.String(255))
    user_colour: db.Column = db.Column(db.String(255))
    dark_mode: db.Column = db.Column(db.Boolean, default=False)
    
class SettingsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Settings
        load_instance = True
        include_fk = True