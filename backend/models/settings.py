from models import db

class Settings(db.Model):
    __tablename__ = "settings"
    
    user_id: db.Column = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False,primary_key=True,)
    background_colour: db.Column = db.Column(db.String(255))
    accent_colour: db.Column = db.Column(db.String(255))
    font: db.Column = db.Column(db.String(255))
    user_colour: db.Column = db.Column(db.String(255))
    dark_mode: db.Column = db.Column(db.Boolean, default=False)