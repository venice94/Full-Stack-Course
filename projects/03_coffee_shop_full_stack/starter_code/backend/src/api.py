import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import traceback

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    return jsonify({"success":True, "drinks":[drink.short() for drink in drinks]})

@app.route('/drinks-detail', methods=['GET'])
@requires_auth(permission='get:drinks-detail')
def get_drink_details():
    drinks = Drink.query.all()
    if drinks is None:
        abort(404)

    return jsonify({"success":True, "drinks":[drink.long() for drink in drinks]})

@app.route('/drinks', methods=['POST'])
@requires_auth(permission='post:drinks')
def add_drink(permission):
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    if new_title is None or new_recipe is None:
        abort(404)

    try:
        new_drink=Drink(title=new_title,recipe=new_recipe)
        print(type(new_drink))
        print(new_drink.title)
        print(new_drink.recipe)
        new_drink.insert()

    except:
        abort(422)

    return jsonify({"success":True, "drinks":[new_drink.short() for drink in new_drink]})

@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth(permission='patch:drinks')
def edit_drink(id):
    drink_id = id
    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)

    try:
        if new_title is not None:
            drink.title = new_title
            drink.update()
        
        if new_receipe is not None:
            drink.recipe = new_recipe
            drink.update()

    except:
        abort(422)

    return jsonify({"success":True, "drinks":[drink.long() for drink in drinks]})

@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth(permission='delete:drinks')
def delete_drink(id):
    drink_id = id

    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()
    except:
        abort(422)

    return jsonify({"success":True, "delete":drink_id})

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def unprocessable(AuthError):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorised"
    }), 401