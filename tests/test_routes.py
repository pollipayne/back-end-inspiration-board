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
    

def test_update_single_card(client, three_cards):
    #act
    response = client.put("cards/3", json={"message": "updated message"})
    response_body = response.get_json()

    #assert 
    assert response.status_code == 201
    assert "card" in response_body
    assert response_body == {"card": {
        "id": 3,
        "message": "updated message",
        "likes_count": 0,
        "board_id": None
    }}


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

def test_post_card_to_board_no_cards(client, one_board, one_card): 
    # Act
    response = client.post("/boards/1/cards", json={
        "message": "Test message"
    })

    response_body = response.get_json() 

    associated_board = Board.query.get(response_body["card"]["board_id"]) 
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

    response_body = response.get_json() 

    associated_board = Board.query.get(response_body["card"]["board_id"]) 
    associated_board = associated_board.format_to_json()

    # Assert
    assert response.status_code == 201
    assert len(associated_board["associated_cards"]) == 2
    assert bool(response_body) == True
    assert response_body["card"]["board_id"] == associated_board["id"] 
    assert "card" in response_body

