from app import db


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(40), nullable=False)
    likes_count = db.Column(db.Integer)