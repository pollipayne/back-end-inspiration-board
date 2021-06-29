from app import db

class Board(db.Model):
    __name__ = 'board'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    owner = db.Column(db.String)

    def format_to_json(self):
        return {
                "id": self.id, 
                "title": self.title,
                "owner": self.owner
            }