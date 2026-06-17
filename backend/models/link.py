from marshmallow import Schema, fields

from models import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

#id #pimary key
#from_article_id
#to_article_id #can be null
#type_string #can be empty
#link in the content is of the form @{link_id} but is placed via @ or [[]]


#When we create a link we have to somehow ensure that only one link is registered in the database but mulitple work for navigation

class Links(db.Model):
    __tablename__ = "links"
    unique_link_id: db.Column = db.Column(db.String(255),primary_key=True)
    waiting: db.Column = db.Column(db.Boolean, default=True)
    to_string: db.Column = db.Column(db.String(255), nullable=False)
    from_article_id: db.Column = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    to_article_id: db.Column = db.Column(db.Integer, db.ForeignKey("articles.id"))
    type_string: db.Column = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f"id={self.id!r}, from_article_id={self.from_article_id!r}, to_article_id={self.to_article_id!r}, type_string={self.type_string!r})"

def get_unique_link_id(from_article_id, to_article_id=None, to_string=None):
    return f"{from_article_id}_{to_article_id if to_article_id else to_string}"


class LinkDataSchema(Schema):
    from_article_id = fields.Int(required=True)
    to_article_id = fields.Int()
    to_string = fields.Str()
    type_string = fields.Str()
    
class LinkToUpdateSchema(Schema):
    to_article_id = fields.Int()
    to_string = fields.Str()
    type_string = fields.Str()
    

class LinksSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Links
        load_instance = True
        include_fk = True