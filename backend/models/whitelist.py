from models import db
from marshmallow import Schema, fields

class Whitelist(db.Model):
    __tablename__ = "whitelist"
    
    email: db.Column = db.Column(db.String(255), primary_key=True)

class WhitelistSchema(Schema):
    emails = fields.Str()


def _is_email_whitelisted(email):
    whitelist_entry = Whitelist.query.get(email)
    if whitelist_entry is not None:
        return True

    return False