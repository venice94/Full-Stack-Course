import os
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.sqltypes import Date, DateTime, Float
from flask_sqlalchemy import SQLAlchemy
import json
from datetime import date

db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    db.create_all()

    user = User(
        name='Test User',
        created_date=date.today(),
        )
    user.insert()

    shop = Shop(
        name='ABC Bookstore',
        industry='Retail',
        address='123 Studious Street'
    )
    shop.insert()

class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    created_date = Column(Date, nullable = False)
    status = Column(String(10), nullable = False, default = 'Active')
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic')

    def __init__(self, id, name, created_date, status):
        self.id = id
        self.name = name
        self.created_date = created_date
        self.status = status

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
        'id': self.id,
        'name': self.name,
        'created_date': self.created_date,
        'status': self.status
        }

class Shop(db.Model):
    __tablename__ = 'shop'

    id = Column(Integer, primary_key = True)
    name = Column(String(50), nullable = False)
    industry = Column(String(50), nullable = True)
    address = Column(String(100), nullable = True)
    transactions = db.relationship('Transaction', backref='shop', lazy='dynamic')
    
    def __init__(self, id, name, industry, address):
        self.id = id
        self.name = name
        self.industry = industry
        self.address = address

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
        'id': self.id,
        'name': self.name,
        'industry': self.industry,
        'address': self.address
        }

class Transaction(db.Model):  
  __tablename__ = 'transaction'

  id = Column(Integer, primary_key=True)
  type = Column(String(50), nullable = False)
  amount = Column(Float, nullable = False)
  category = Column(String(50), nullable = False)
  status = Column(String(10), nullable = False, default = 'Active')
  date = Column(Date, nullable = False)
  description = Column(String(120), nullable = True)
  user_id = Column(Integer, db.ForeignKey('User.id'), nullable = False)
  shop_id = Column(Integer, db.ForeignKey('Shop.id'), nullable = True)

  def __init__(self, id, type, amount, category, status, date, description, user_id, shop_id):
    self.id = id
    self.type = type
    self.amount = amount
    self.category = category
    self.status = status
    self.date = date
    self.description = description
    self.user_id = user_id
    self.shop_id = shop_id

  def insert(self):
    db.session.add(self)
    db.session.commit()
  
  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'type': self.type,
      'amount': self.amount,
      'category': self.category,
      'status': self.status,
      'date': self.date,
      'description': self.description,
      'user_id': self.user_id,
      'shop_id': self.shop_id
    }
