from app.models.board import Board
import pytest
from app import create_app
from app import db
from app.models.card import Card


@pytest.fixture
def app():
    # create the app with a test config dictionary
    app = create_app({"TESTING": True})

    with app.app_context():
        db.create_all()
        yield app

    # close and remove the temporary database
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


#This fixture creates one card and saves it to the DB 
@pytest.fixture
def one_card(app):
    new_card = Card(
        message="Noodles are the best."
    )
    db.session.add(new_card)
    db.session.commit()

# This fixture creates multiple cards and saves to DB 
@pytest.fixture
def three_cards(app):
    db.session.add_all([Card( message="Hey, you're awesome"), 
                        Card(message="Where are my glasses?"), 
                        Card(message="Something inspirational")])

    db.session.commit()


# This fixture creates a board and saves to DB 
@pytest.fixture
def one_board(app):
    new_board = Board(title="Wild Board", owner="LAC")
    db.session.add(new_board)
    db.session.commit()

# This fixture creates several boards and saves to DB 
@pytest.fixture
def three_boards(app):
    db.session.add_all([
        Board(title="Pensive Board", owner="KFC"),
        Board(title="Bored Board", owner="QAB"),
        Board(title="Happy Board", owner="ANA")])
    db.session.commit()


# This fixture connects a card to the appropriate board and saves to DB
@pytest.fixture
def one_card_belongs_to_one_board(app, one_card, one_board):
    card = Card.query.first()
    board = Board.query.first()
    board.associated_cards.append(card)
    db.session.commit()