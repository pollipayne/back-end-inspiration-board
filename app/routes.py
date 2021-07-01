from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.card import Card
from app.models.board import Board 
import requests
import os 



card_bp = Blueprint("cards", __name__, url_prefix='/cards')
board_bp = Blueprint("boards", __name__, url_prefix="/boards")

# >>>>>>> CRUD FOR CARDS BELOW >>>>>>>>
@card_bp.route("", methods=["GET"])
def get_all_cards():
    """A BE only endpoint to check on card functionality"""

    cards = Card.query.all()

    card_response = []

    for card in cards:
        card_response.append(card.to_json())
    return jsonify(card_response) 


@card_bp.route("/<card_id>", methods=["GET"]) 
def get_single_card(card_id):
    """Get a single card by ID"""

    card = Card.query.get(card_id)

    if card is None:
        return make_response({"details": "Invalid ID"}, 404)
    return {'card': card.to_json()}


@card_bp.route("/<card_id>/upvote", methods=["PUT"]) 
def upvote_single_card(card_id):
    """Upvote a single card by ID"""

    card = Card.query.get(card_id)

    if not card:
        return make_response({"details": "Invalid ID"}, 404)

    card.likes_count += 1

    db.session.commit()
    return {'card': card.to_json()}


@card_bp.route("/<card_id>", methods=["PUT"])
def update_single_card(card_id):
    """Edit a single card by ID"""
    request_body = request.get_json()

    card = Card.query.get(card_id)
    
    if not card:
        return make_response({"details": "Invalid ID"}, 404)
    if len(request_body["message"]) > 40:
        return make_response({"details": "Message must be 40 characters or less."})

    card.message = request_body["message"]

    db.session.add(card)
    db.session.commit()
    return {'card': card.to_json()}, 201

    
@card_bp.route("/<card_id>", methods=["DELETE"])
def delete_single_card(card_id):
    """Delete a single card by ID"""

    card = Card.query.get(card_id)
    if card is None:
        return make_response({"details": "Invalid ID"}, 404)

    db.session.delete(card)
    db.session.commit()
    return {"details": f"Card with ID #{card_id} has been deleted."}



# >>>>>>> CRUD FOR BOARDS BELOW >>>>>>>>
@board_bp.route("", methods=["POST"])
def create_board():
    """Create a board for cards to be posted on"""
    request_body = request.get_json()

    if "title" not in request_body or "owner" not in request_body:
        return make_response({"details": "Invalid data"}, 400)

    new_board = Board(title=request_body["title"],
                    owner=request_body["owner"])

    db.session.add(new_board)
    db.session.commit()
    return {'board': new_board.format_to_json()}, 201


@board_bp.route("", methods=["GET"])
def get_all_boards():
    """Get all boards"""
    boards = Board.query.all()

    hold_boards = []
    if not boards:
        return jsonify(hold_boards) 

    for board in boards:
        hold_boards.append(board.format_to_json())
    return jsonify(hold_boards)


@board_bp.route("/<board_id>", methods=["GET"])
def get_single_board(board_id):
    """ Get single board and its data"""
    single_board = Board.query.get(board_id)

    if not single_board:
        return make_response("", 404)
    return {'board': single_board.format_to_json()}


@board_bp.route("/<board_id>", methods=["DELETE"]) 
def delete_single_board(board_id):
    """Delete specific board"""
    board = Board.query.get(board_id)
    if not board:
        return make_response({"details": "Invalid ID"}, 404)

    db.session.delete(board)
    db.session.commit()
    return {"details": f"Board with ID #{board_id} has been deleted."}


# >>>>>>> ONE TO MANY ENDPOINTS BELOW >>>>>>>>
@board_bp.route("/<board_id>/cards", methods=["GET"])
def get_all_cards_for_board(board_id):

    board = Board.query.get(board_id)

    if board is None:
        return make_response({"details": "Invalid ID"}, 404)

    card_list = []

    try:
        for card in board.associated_cards: 
            card = card.to_json()
            card_list.append(card)
    except: 
        return make_response({"details": "There are no associated cards for this board. "})
    return jsonify(card_list)

### post a card to a specific board - LC
@board_bp.route("/<board_id>/cards", methods=["POST"])
def create_card_for_board(board_id):
    board_id = int(board_id)
    relevant_board = Board.query.get(board_id)
    hold_card_ids = []

    request_body = request.get_json()
    new_card = Card.new_card_from_json(request_body)
    
    if not new_card.message:
        return make_response({"details": "Invalid Data"}, 400)
    if len(new_card.message) > 40:
        return make_response({"details": "Message must be 40 characters or less."}, 400)
    db.session.add(new_card) 

    # link to board
    relevant_board.associated_cards.append(new_card)
    
    for card in relevant_board.associated_cards:
        hold_card_ids.append(card.id)
    db.session.commit()

    return {'card': new_card.to_json()}, 201 # >>> shows the card that was successfully posted
    #return make_response({"id": board_id, "associated_card_ids": hold_card_ids}, 201) # shows the list of ids for arbit test >>> or 200; tlapi test called for 200