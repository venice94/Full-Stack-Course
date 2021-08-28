from models import Wallet_User, Shop, Transaction, setup_db, db_drop_and_create_all
from auth import requires_auth
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date
from auth import AuthError, requires_auth

app = Flask(__name__)
CORS(app)

app.config.from_object('config')
db = SQLAlchemy()
setup_db(app)

db_drop_and_create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

ROWS_PER_PAGE = 10
TRANSACTION_TYPE = ['Income', 'Expense']

def paginate_row(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * ROWS_PER_PAGE
  end = start + ROWS_PER_PAGE

  rows = [row.format() for row in selection]
  current_results = rows[start:end]

  return current_results


@app.route('/user-page', methods= ['GET'])
def user_authenticated():
  return "You have successfully logged in."


@app.route('/users', methods = ['GET'])
@requires_auth('get:all-users')
def get_all_users(token):
  users = Wallet_User.query.all()
  if users is None:
    abort(404)

  return jsonify({
    'success': True,
    'user': paginate_row(request, users)
    })


@app.route('/shops', methods = ['GET'])
def get_all_shops():
  shops = Shop.query.all()
  if shops is None:
    abort(404)

  return jsonify({
    'success': True,
    'shop': paginate_row(request, shops)
    })


@app.route('/users/<user_id>', methods = ['GET'])
@requires_auth('get:user')
def get_one_user(token, user_id):
  user = Wallet_User.query.filter(Wallet_User.id == user_id).one_or_none()
  if user is None:
    abort(404)

  return jsonify({
    'success': True,
    'user': user.format()
    })


@app.route('/users/<user_id>/transactions', methods = ['GET'])
@requires_auth('get:user-transactions')
def get_user_transactions(token, user_id):
  selection = Transaction.query.filter(Transaction.user_id == user_id).all()
  if selection is None:
    abort(404)
  
  transactions = paginate_row(request, selection)

  return jsonify({
    'success': True,
    'user_id': user_id,
    'transactions': transactions
    })


@app.route('/users/<user_id>', methods = ['PATCH'])
@requires_auth('patch:user')
def edit_user(token, user_id):
  user = Wallet_User.query.filter(Wallet_User.id == user_id).one_or_none()
  if user is None:
    abort(404)
  
  body = request.get_json()

  new_name = body.get('name', None)
  new_status = body.get('status', None)
  
  if new_name is not None:
      try:
          user.name = new_name
          user.update()
      except Exception:
          abort(422)
  
  if new_status is not None:
      try:
          user.status = new_status
          user.update()
      except Exception:
          abort(422)

  return jsonify({
    'success': True,
    'user': user.format()
  })


@app.route('/users/<user_id>/transactions', methods = ['POST'])
@requires_auth('post:user-transactions')
def add_user_transaction(token, user_id):
  body = request.get_json()

  new_type = body.get('type', None)
  new_amount = body.get('amount', None)
  new_category = body.get('category', None)
  new_description = body.get('description', None)
  new_shop_id = body.get('shop_id', None)

  if new_type is None or new_amount is None or new_category is None:
    abort(404)

  if new_type not in TRANSACTION_TYPE:
    abort(422)
  
  new_transaction = Transaction(
    type=new_type,
    amount=new_amount,
    category=new_category,
    date=date.today(),
    description=new_description,
    user_id=user_id,
    shop_id=new_shop_id
  )

  try:
      new_transaction.insert()
  except Exception:
      abort(422)
  
  return jsonify({
    'success': True,
    'transaction': new_transaction.format()
  })

  
@app.route('/users/<user_id>', methods = ['DELETE'])
@requires_auth('delete:user')
def delete_user(token, user_id):
  user = Wallet_User.query.filter(Wallet_User.id == user_id).one_or_none()
  if user is None:
    abort(404)

  try:
      user.delete()
  except Exception:
      abort(422)

  return jsonify({
    'success': True,
    'deleted': user.format()
    })


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
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def unprocessable(AuthError):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorised"
    }), 401
