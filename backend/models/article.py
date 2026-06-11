from models import db

class Articles(db.Model):
    __tablename__ = "articles"

    id: db.Column = db.Column(db.Integer, primary_key=True)
    folder_id: db.Column = db.Column(db.Integer, db.ForeignKey("folders.id"))
    author_id: db.Column = db.Column(db.String(255), db.ForeignKey("user_account.id"))
    title: db.Column = db.Column(db.String(255), nullable=False, unique=True)
    content: db.Column = db.Column(db.String(255))
    permitted_usernames: db.Column = db.Column(db.String(255))
    parent_article_id: db.Column = db.Column(db.Integer, db.ForeignKey("articles.id"))
    children = db.relationship("Articles", backref=db.backref("parent", remote_side=[id]))

    def __repr__(self) -> str:
        return f"id={self.id!r}, title={self.title!r}, content={self.content!r})"
