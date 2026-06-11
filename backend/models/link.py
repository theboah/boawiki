from models import db

#id #pimary key
#from_article_id
#to_article_id #can be null
#type_string #can be empty
#link in the content is of the form @{link_id} but is placed via @ or [[]]


#When we create a link we have to somehow ensure that only one link is registered in the database but mulitple work for navigation

class Links(db.Model):
    __tablename__ = "links"

    id: db.Column = db.Column(db.Integer, primary_key=True)
    unique_link_id: db.Column = db.Column(db.String(255), unique=True, nullable=False)
    waiting: db.Column = db.Column(db.Boolean, default=True)
    to_string: db.Column = db.Column(db.String(255), nullable=False)
    from_article_id: db.Column = db.Column(db.Integer, db.ForeignKey("articles.id"), nullable=False)
    to_article_id: db.Column = db.Column(db.Integer, db.ForeignKey("articles.id"))
    type_string: db.Column = db.Column(db.String(255), nullable=False)

    def __repr__(self) -> str:
        return f"id={self.id!r}, from_article_id={self.from_article_id!r}, to_article_id={self.to_article_id!r}, type_string={self.type_string!r})"