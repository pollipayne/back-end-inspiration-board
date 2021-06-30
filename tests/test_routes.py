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
def test_get_boards_no_saved_boards(client):
    # Act
    response = client.get("/boards")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert response_body == []

def test_get_boards_three_saved_boards(client, three_boards):
    #act
    response = client.get('/boards')
    response_body = response.get_json()

    #assert 
    assert response.status_code == 200 
    assert len(response_body)  == 3
    assert response_body == [
        {
            "id": 1,
            "title": "Pensive Board",
            "owner": "KFC",
            "associated_cards": []
            },
            {
            "id": 2,
            "title": "Bored Board",
            "owner": "QAB",
            "associated_cards": []
            }, {
            "id": 3,
            "title": "Happy Board",
            "owner": "ANA",
            "associated_cards": []
            } 
    ]

def test_get_board_by_ID(client, one_board):
    # Act
    response = client.get("/boards/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 200
    assert len(response_body) == 1
    assert "board" in response_body
    assert response_body == {
        "board": {
            "id": 1,
            "title": "Wild Board",
            "owner": "LAC",
            "associated_cards": []
            }
    }

def test_get_board_not_found(client):
    # Act
    response = client.get("/boards/1")
    response_body = response.get_json()

    # Assert
    assert response.status_code == 404
    assert response_body == None

def test_create_board_must_contain_title(client):
    # Act
    response = client.post("/boards", json={
                "owner": "Test owner name"
            })
    response_body = response.get_json()

    # Assert
    assert response.status_code == 400
    assert "details" in response_body
    assert response_body == {
        "details": "Invalid data"
    }
    assert Board.query.all() == []

def test_create_board_must_contain_owner(client): 
    # Act
    response = client.post("/boards", json={
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

# following tests check that: card(s) exist(s), that they belong to right board, that the asso'card list lengthens w each addtl card
def test_post_card_to_board_no_cards(client, one_board, one_card): 
    # Act
    response = client.post("/boards/1/cards", json={
        "message": "Test message"
    })

    response_body = response.get_json() # {'card': {'board_id': 1, 'id': 4, 'likes_count': 0, 'message': 'Test message'}}

    associated_board = Board.query.get(response_body["card"]["board_id"]) # {'id': 1, 'title': 'Build a habit of going outside daily', 'owner': 'LAC', 'associated_cards': [<Card 4>]}
    associated_board = associated_board.format_to_json() 
    
    # Assert
    assert response.status_code == 201
    assert bool(response_body) == True
    assert response_body["card"]["board_id"] == associated_board["id"]
    assert "card" in response_body

def test_post_card_to_board_already_with_cards(client, one_card_belongs_to_one_board, three_cards):
    # Act
    response = client.post("/boards/1/cards", json={
        "message": "Test message"
        })

    response_body = response.get_json() # {'card': {'board_id': 1, 'id': 5, 'likes_count': 0, 'message': 'Test message'}}

    associated_board = Board.query.get(response_body["card"]["board_id"]) 
    associated_board = associated_board.format_to_json() # {'id': 1, 'title': 'Build a habit of going outside daily', 'owner': 'LAC', 'associated_cards': [<Card 1>, <Card 5>]}

    # Assert
    assert response.status_code == 201
    assert len(associated_board["associated_cards"]) == 2
    assert bool(response_body) == True
    assert response_body["card"]["board_id"] == associated_board["id"] 
    assert "card" in response_body

# IF ENDPOINT'S KEPT/THERE'S TIME
    # test_update_board
    # test_update_board_doesnt_exist
    # test_delete_board
    # test_delete_board_doesnt_exist
    # test get_boards_sorted_asc
    # test get_boards_sorted_desc