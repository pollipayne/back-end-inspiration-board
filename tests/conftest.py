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
    db.session.add_all([Card( message="Hey, you're awesome"), Card(message="Where are my glasses?"), Card(message="Something inspirational")])

    db.session.commit()


