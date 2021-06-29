from flask import Blueprint, request, jsonify, make_response
from app import db
from app.models.card import Card
import requests
import os 

# example_bp = Blueprint('example_bp', __name__)


card_bp = Blueprint("cards", __name__, url_prefix='/cards')



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