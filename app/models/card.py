from app import db
from flask import current_app


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(40), nullable=False)
    likes_count = db.Column(db.Integer)



    def to_json(self):
        card_dictionary = {
            'id': self.id, 
            "message": self.message, 
            "likes_count": self.likes_count
        }

        return card_dictionary


    @classmethod
    def new_card_from_json(cls, body):
        new_card = Card(message=body['message'], likes_count=body['likes_count'])
        return new_card