from flask.wrappers import Response
from app.models.card import Card 
from app.models.board import Board
import unittest # may not need - LC
from unittest.mock import Mock, patch # may not need - LC


def test_get_all_cards_no_saved_cards(client):
    #act 
    response = client.get("/cards")
    response_body = response.get_json()

    #assert
    assert response.status_code == 200
    assert response_body == []


def test_get_cards_one_saved_card(client, one_card):
    #act
    response = client.get("/cards")
    response_body = response.get_json()

    #assert 
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 1, 
            "message": "Noodles are the best.",
            "likes_count": 0,
            "board_id": None
        }
    ]

def test_get_cards_three_saved_cards(client, three_cards):
    #act
    response = client.get('/cards')
    response_body = response.get_json()

    #assert 
    assert response.status_code == 200 
    assert len(response_body)  == 3
    assert response_body == [
        {
        "id": 1, 
        "message": "Hey, you're awesome",
        "likes_count": 0,
        "board_id": None

    },{
        "id": 2, 
        "message": "Where are my glasses?",
        "likes_count": 0,
        "board_id": None
    }, {
        "id": 3, 
        "message": "Something inspirational",
        "likes_count": 0,
        "board_id": None
    } 
    ]


def test_delete_card_three_saved_cards(client, three_cards):
    #act
    response = client.delete("/cards/3")
    response_body = response.get_json()
    check_for_deletion = client.get("/cards")
    check_response_body = check_for_deletion.get_json()


    #assert
    assert response.status_code == 200 
    assert len(check_response_body) == 2
    assert response_body == {"details": "Card with ID #3 has been deleted."}


def test_get_card_not_found(client):
    #act
    response = client.get('/cards/1')
    response_body = response.get_json()

    #assert
    assert response.status_code == 404
    assert response_body == {"details": "Invalid ID"}


def test_upvote_card(client, one_card):
    #act
    response = client.put("/cards/1/upvote")

    response_body = response.get_json()

    #assert 
    assert response.status_code == 200
    assert "card" in response_body
    assert response_body == {
        "card": {
            "id": 1,
            "message": "Noodles are the best.",
            "likes_count": 1,
            "board_id": None  
        }
    }

def test_upvote_card_not_found(client):
    #act
    response = client.put("cards/1/upvote")
    response_body = response.get_json()

    #assert 
    assert response.status_code == 404
    assert response_body == {"details": "Invalid ID"}


# LC test adds 

# test_get_all_boards_no_boards_created
def test_get_boards_no_saved_boards(client):
    # Act
    response = client.get("/boards")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == []

# test_get_all_boards_one_board_created
def test_get_boards_one_saved_board(client, one_board):
    # Act
    response = client.get("/boards")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert response_body == [
        {
            "id": 1, # ID included on task list tests, okay to replicate?
            "title": "Build a habit of going outside daily",
            "owner": "LAC"
            }
    ]

# test_get_single_board
def test_get_board(client, one_board):
    # Act
    response = client.get("/boards/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert "board" in response_body
    assert response_body == {
        "board": {
            "id": 1,
            "title": "Build a habit of going outside daily",
            "owner": "LAC"
            }
    }

# test_get_single_board_doesnt_exist
def test_get_board_not_found(client):
    # Act
    response = client.get("/boards/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body == None

# test_create_board
    # redundant? 

#CHECK POST BOARD ROUTES TO SEE THAT THESE PASS
# test_create_board_missing_title
def test_create_board_must_contain_title(client):
    # Act
    response = client.post("/boards", json={ # client offers board post attempt without title
                "owner": "Test owner name"
            })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "details" in response_body
    assert response_body == {
        "details": "Invalid data"
    }
    assert Board.query.all() == [] # should not populate bc incorrectly submitted

# test_create_board_missing_owner  >>> necessary? allowing anon submissions?
def test_create_board_must_contain_owner(client): 
    # Act
    response = client.post("/boards", json={ # client offers board post attempt without owner
                "title": "Test title"
            })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "details" in response_body
    assert response_body == {
        "details": "Invalid data"
    }
    assert Board.query.all() == []

# UNFINSIHED BELOW - LC, 6.29, 11:50pm
# test_post_card_to_board (make sure data populates to associated_cards attr in Board table)
# How-To??
def test_post_card_to_board(client, one_board, three_cards):
    # Act
    response = client.post("/boards/1/cards", json={ # "boards/<board_id>/cards"
        "message": "Test message", # bc Card class method, offered as request_body in route
        "likes_count": 0
        #"associated_card_ids": [1, 2, 3] # this is not a Card attr
    })

    response_body = response.get_json()
    print('EYYE: ', response_body) # EYYE: {'associated_card_ids': [4], 'id': 1}

    # Assert
    assert response.status_code == 201
    assert "id" in response_body # as in board id
    assert "associated_card_ids" in response_body
    assert response_body == {
        "id": 1,
        "associated_card_ids": [1, 2, 3]
    }

    # Check that board column was updated in the db
    assert len(Board.query.get(1).associated_cards) == 3

# test_post_card_to_board_that_already_has_cards ("", properly adding to list)
    # HOW-TO?

# IF ENDPOINT'S KEPT/THERE'S TIME
    # test_update_board
    # test_update_board_doesnt_exist
    # test_delete_board
    # test_delete_board_doesnt_exist
    # test get_boards_sorted_asc
    # test get_boards_sorted_desc