from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.card import Card
from app.models.board import Board
import requests
import os 
from sqlalchemy import desc, asc # unsolicited board sorting functionality - LC

# example_bp = Blueprint('example_bp', __name__)

card_bp = Blueprint("cards", __name__, url_prefix='/cards')
board_bp = Blueprint("boards", __name__, url_prefix="/boards")

# >>>>>>> CRUD FOR CARDS BELOW >>>>>>>>

#GET requests/all cards for a single board (return a list of card dictionaries?)
@card_bp.route("", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()

    card_response = []

    for card in cards:
        card_response.append(card.to_json())
    return jsonify(card_response), 200 

# GET request for single card by id (in order to delete? )
@card_bp.route("/<card_id>", methods=["GET"])
def get_single_card(card_id):
    card = Card.query.get(card_id)

    if card is None:
        return make_response({'details':"invalid ID"}, 404)
    
    return {'card': card.to_json()}



# POST requests (create a new card for selected board)
@card_bp.route("", methods=["POST"])
def post_new_card():
    request_body = request.get_json()

    try:
        new_card = Card.new_card_from_json(request_body)
    except KeyError: 
        return make_response({"details": "Invalid Data"}, 400)
    
    db.session.add(new_card)
    db.session.commit()

    return make_response({'card': new_card.to_json()}, 201)



#DELETE requests (delete an existing card )
@card_bp.route("/<card_id>", methods=["DELETE"])
def delete_single_card(card_id):

    card = Card.query.get(card_id)
    if card is None:
        return make_response({"error": "invalid ID"}, 404)

    db.session.delete(card)
    db.session.commit()

    return make_response({"details": f"Card with {card_id} has been deleted."}, 200)


### notes for standup - figure out how to implement board relationship so we can select cards by the board id to only effect cards for the selected board. Get together with Lauren to determine a synchronized format for 404 responses, JSON data shape, etc. 
## LC standup notes: unsolicited additions (marked below): sorting boards when GETting them, updating a board, deleting board(s) -- can remove if it doesnt make sense for front end




######### LAC ADDITIONS BELOW #########
# BOARD CRUD ROUTES - LC
@board_bp.route("", methods=["POST"])
def create_board():
    """Create a board for cards to be posted on"""
    request_body = request.get_json()

    if "title" not in request_body or "owner" not in request_body:
        return make_response({"details": "Invalid data. Must include both title and owner name."}, 400) # dictated by tlapi tests!
    
    new_board = Board(title=request_body["title"],
                    owner=request_body["owner"])

    db.session.add(new_board)
    db.session.commit()
    return jsonify(new_board.format_to_json()), 201

@board_bp.route("", methods=["GET"])
def get_all_tasks():
    """Get all boards"""
    boards_ordered = request.args.get("sort") # sort the boards, unsolicited extra mini-feature - LC

    if not boards_ordered:
        boards = Board.query.all()
    elif boards_ordered == "asc":
        boards = Board.query.order_by(asc(Board.title))
    elif boards_ordered == "desc":
        boards = Board.query.order_by(desc(Board.title))

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
    return jsonify(single_board.format_to_json()) # default 200 code okay? 

@board_bp.route("/<board_id>", methods=["PUT"]) # not in instructions but why couldnt we update a board?
def update_single_board(board_id):
    """Overwrites a board with details provided by user"""
    board = Board.query.get(board_id)

    if not board:
        return make_response("", 404)

    request_body = request.get_json()
    board.title = request_body["title"]
    board.owner = request_body["owner"]

    db.session.commit()
    return jsonify(board.format_to_json())

@board_bp.route("/<board_id>", methods=["DELETE"]) # not in instructions, but on Simon's site
def delete_single_board(board_id):
    """Delete specific board"""
    board = Board.query.get(board_id)
    if not board:
        return make_response("", 404)

    db.session.delete(board)
    db.session.commit()
    return make_response({"details": f'The "{board.title}" board has been deleted'}, 200)