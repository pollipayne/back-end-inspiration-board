from app import db


class Board(db.Model):
    __name__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    owner = db.Column(db.String)