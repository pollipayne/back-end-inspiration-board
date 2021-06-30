from flask.wrappers import Response
from app.models.card import Card 
from app.models.board import Board


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
# test_get_all_boards_one_board_created
# test_get_single_board
# test_get_board_doesnt_exist
# test_create_board
# test_create_board_missing_title
# test_create_board_missing_owner  >>> necessary?
# test_post_card_to_board (make sure data populates to associated_board attr in Card table)
# test_post_card_to_board_that_already_has_cards ("", properly adding to list)

# IF ENDPOINT'S KEPT/THERE'S TIME
    # test_update_board
    # test_update_board_doesnt_exist
    # test_delete_board
    # test_delete_board_doesnt_exist
    # test get_boards_sorted_asc
    # test get_boards_sorted_desc