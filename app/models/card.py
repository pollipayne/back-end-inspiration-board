from app import db


class Card(db.Model):
    __name__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(40))
    likes_count = db.Column(db.Integer)