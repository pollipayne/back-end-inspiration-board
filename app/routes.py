from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.card import Card
from app.models.board import Board 
import requests
import os 
from sqlalchemy import desc, asc # unsolicited board sorting functionality - LC

card_bp = Blueprint("cards", __name__, url_prefix='/cards')
board_bp = Blueprint("boards", __name__, url_prefix="/boards")

# >>>>>>> CRUD FOR CARDS BELOW >>>>>>>>

#GET requests/all cards (probably won't be needed)
@card_bp.route("", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()

    card_response = []

    for card in cards:
        card_response.append(card.to_json())
    return jsonify(card_response) # took off 200, bc default status code - LC


# GET request for single card by id (probably won't be needed)
@card_bp.route("/<card_id>", methods=["GET"]) 
def get_single_card(card_id):
    card = Card.query.get(card_id)

    if card is None:
        return make_response({"details": "Invalid ID"}, 404)
    return {'card': card.to_json()}



#PUT FOR UPVOTES  request for single card by id && increase upvote count 
@card_bp.route("/<card_id>/upvote", methods=["PUT"]) 
def update_single_card(card_id):

    card = Card.query.get(card_id)

    if not card:
        return make_response({"details": "Invalid ID"}, 404)


    card.likes_count += 1

    db.session.commit()
    return {'card': card.to_json()}



# POST requests - single card (probably won't be needed)
@card_bp.route("", methods=["POST"])
def post_new_card():
    request_body = request.get_json()

    try:
        new_card = Card.new_card_from_json(request_body)
    except KeyError: 
        return make_response({"details": "Invalid ID"}, 404)
    if len(new_card.message) > 40:
        return make_response({"details": "Message must be 40 characters or less."})
    
    db.session.add(new_card)
    db.session.commit()
    return {'card': new_card.to_json()}, 201
    #return make_response({'card': new_card.to_json()}, 201) -- original



#DELETE requests (delete an existing card)
@card_bp.route("/<card_id>", methods=["DELETE"])
def delete_single_card(card_id):

    card = Card.query.get(card_id)
    if card is None:
        return make_response({"details": "Invalid ID"}, 404)

    db.session.delete(card)
    db.session.commit()
    return {"details": f"Card with ID #{card_id} has been deleted."}
    #return make_response({"details": f"Card with ID #{card_id} has been deleted."}, 200) -- original


## LC standup notes: unsolicited additions (marked below): sorting boards when GETting them, updating a board, deleting board(s) -- can remove if it doesnt make sense for front end


######### LAC ADDITIONS BELOW #########
# BOARD CRUD ROUTES - LC
@board_bp.route("", methods=["POST"])
def create_board():
    """Create a board for cards to be posted on"""
    request_body = request.get_json()

    if "title" not in request_body or "owner" not in request_body:
        return make_response({"details": "Invalid data"}, 400)
        # changed for tests: return make_response({"details": "Invalid data. Must include both title and owner name."}, 400) # per instructions
    
    new_board = Board(title=request_body["title"],
                    owner=request_body["owner"])

    db.session.add(new_board)
    db.session.commit()
    return {'board': new_board.format_to_json()}, 201
    #return make_response({'board': new_board.format_to_json()}, 201) -- matches BP's orig
    #return jsonify(new_board.format_to_json()), 201  -- original

@board_bp.route("", methods=["GET"])
def get_all_boards():
    """Get all boards"""
    boards_ordered = request.args.get("sort") # sort the boards, unsolicited extra mini-feature - LC

    if not boards_ordered:
        boards = Board.query.all()
    elif boards_ordered == "asc":
        boards = Board.query.order_by(asc(Board.title))
    elif boards_ordered == "desc":
        boards = Board.query.order_by(desc(Board.title)) # leave for now

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
    #return jsonify({'board': single_board.format_to_json()}) -- original

@board_bp.route("/<board_id>", methods=["PUT"]) # not in instructions but why couldnt we update a board?
def update_single_board(board_id):
    """Overwrites a board with details provided by user"""
    board = Board.query.get(board_id)

    if not board:
        return make_response({"details": "Invalid ID"}, 404)

    request_body = request.get_json()
    board.title = request_body["title"]
    board.owner = request_body["owner"]

    db.session.commit()
    return {'board': board.format_to_json()}

@board_bp.route("/<board_id>", methods=["DELETE"]) # not in instructions, but on Simon's site
def delete_single_board(board_id):
    """Delete specific board"""
    board = Board.query.get(board_id)
    if not board:
        return make_response({"details": "Invalid ID"}, 404)

    db.session.delete(board)
    db.session.commit()
    return {"details": f"Board with ID #{board_id} has been deleted."}


# ONE-TO-MANY ENDPOINTS

### Get all cards for a selected board 
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
    hold_card_ids = []
    relevant_board = Board.query.get(board_id) # board user will post card to

    request_body = request.get_json() # user offers info for new card, {"message": "blah", "likes_count": 0}
    new_card = Card.new_card_from_json(request_body) # instantiate new card w user data -- BP class method
    
    # from: https://github.com/Ada-C15/full-stack-inspiration-board/blob/main/project-requirements.md 
    # ' See an error message if I try to make a new card with an empty/blank/invalid/missing "message." '
    if not new_card.message: # check to see that actual msg field is empty
        return make_response({"details": "Invalid Data"}, 400)
    if len(new_card.message) > 40: # check to see that msg field has more than 40 chars
        return make_response({"details": "Message must be 40 characters or less."}, 400)
    db.session.add(new_card) 

    # link to board
    relevant_board.associated_cards.append(new_card)
    print('NUM: ', len(relevant_board.associated_cards)) # num of items in asso_card list
    print('ITSELF: ', relevant_board.associated_cards) # list of Card objs [<Card 6>, <Card 7>, <Card 8>...]
    print('can we see it: ', new_card.id) # actual ID! i.e. 34
    
    for card in relevant_board.associated_cards:
        #print('what we want: ', card.id)
        hold_card_ids.append(card.id)
    #print("ASSO'D CARD IDS: ", hold_card_ids)

    db.session.commit()

    #return {'card': new_card.to_json()}, 201 >>> shows the card that was successfully posted
    return make_response({"id": board_id, "associated_card_ids": hold_card_ids}, 201) # shows the list of ids for arbit test >>> or 200; tlapi test called for 200