from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.board import Board # added to allow 'to_json' func - LC
from sqlalchemy import desc, asc # unsolicited board sorting functionality - LC

# UNSOLICITED ADDITIONS: sorting boards when GETting them, updating a board, deleting board(s) -- can remove if it doesnt make sense for front end - LC

# added board blueprint - LC 
board_bp = Blueprint("boards", __name__, url_prefix="/boards")

# BOARD CRUD ROUTES - LC
@board_bp.route("", methods=["POST"])
def create_board():
    """Create a board for cards to be posted on"""
    request_body = request.get_json() # assume dict

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
        hold_boards.append(board.format_to_json()) # formatting func working?
    return jsonify(hold_boards)

@board_bp.route("/<board_id>", methods=["GET"]) # assumed single could be gotten via board ID
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