import os
import unittest
import json
from flask import Flask, request, abort, jsonify
from werkzeug.wrappers import AuthorizationMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import date

from models import setup_db, db_drop_and_create_all, Wallet_User, Shop, Transaction

Manager_jwt = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkhGLUhDSHg2WEI0eU54bS04VlNDSyJ9.eyJpc3MiOiJodHRwczovL2ZzbmQtdmVuaWNlLnVzLmF1dGgwLmNvbS8iLCJzdWIiOiJnb29nbGUtb2F1dGgyfDExMzc0MzA5Mzg5MjUxNzU0ODQxOSIsImF1ZCI6Imh0dHBzOi8vMTI3LjAuMC4xOjUwMDAvd2FsbGV0IiwiaWF0IjoxNjMwMjQ1MjYyLCJleHAiOjE2MzAzMzE2NjIsImF6cCI6IkxqTUdKZ0ozNlBWaktja3M2MnMweThIeHhzbE1EdnZlIiwic2NvcGUiOiIiLCJwZXJtaXNzaW9ucyI6WyJkZWxldGU6dXNlciIsImdldDphbGwtc2hvcHMiLCJnZXQ6YWxsLXVzZXJzIiwiZ2V0OnVzZXIiLCJnZXQ6dXNlci10cmFuc2FjdGlvbnMiLCJwYXRjaDp1c2VyIiwicG9zdDp1c2VyLXRyYW5zYWN0aW9ucyJdfQ.O2OpF6vud-N_-Lt6JS0wg-WbuQVvpWVIuWfSUa11RyM3MiWTQNLC2muiOcBYaAE7fiv9lDVVB6VhAE1opO4h9StFB_3yp_JbXrW_zpiJnMkLh_YT14-mdtXn_x2wI4faw9_KTPS0cKUZEd-dFrV7OIUUVpdHSSpQxoVxS5DOT8a8s6EV9DB3rAmvrcfkTzadGagSXSJ0x98q-uHjEYrsrjTFV0eMNdy2v5qItqPulQiAKLmK-bM7UV5a8FN-ToAlcSrz9PUGLWqB5NXX449k9XN1Zr5anEuNrJXe3F96DADUaJXT54lv_OWVNXvae4y0OPc7i3ejuTc1tCaxWSOWMQ'
    }

class WalletTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = Flask(__name__)
        self.client = self.app.test_client
        self.database_name = "wallet_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('sh_ubuntu', '93water94', 'localhost:5432', self.database_name)

        # binds the app to the current context
        with self.app.app_context():
            setup_db(self.app)
            # create all tables
            db_drop_and_create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_users(self):
        res = self.client().get('/users', headers=Manager_jwt)
        print(res.data)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['users'])
        self.assertTrue(len(data['users']))
    
    def test_404_get_all_users(self):
        res = self.client().get('/users?page=10000', headers=Manager_jwt)
        print(res.data)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_get_all_shops(self):
        res = self.client().get('/shops', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['shops'])
        self.assertTrue(len(data['shops']))
    
    def test_404_get_all_shops(self):
        res = self.client().get('/shops?page=10000', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
    
    def test_get_one_user(self):
        res = self.client().get('/users/1', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success', True])
        self.assertTrue(data['user'])
        self.assertTrue(len(data['user']))

    def test_404_get_one_user(self):
        res = self.client().get('/users/100', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', False])
    
    def test_get_user_transactions(self):
        res = self.client().get('/users/1/transactions', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success', True])
        self.assertTrue(data['user_id'])
        self.assertTrue(data['transactions'])
        self.assertTrue(len(data['transactions']))

    def test_404_get_user_transactions(self):
        res = self.client().get('/users/100/transactions', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', False])
    
    def test_patch_user(self):
        res = self.client().get('/users/1', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success', True])
        self.assertTrue(data['user'])
        self.assertTrue(len(data['user']))
    
    def test_404_patch_user(self):
        res = self.client().get('/users/100', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', False])

    def test_add_user_transaction(self):
        res = self.client().get('/users/1', headers=Manager_jwt, json={
            'type': 'Income',
            'category': 'Salary',
            'amount': 5555.55,
            'description': 'Salary crediting'
        })
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success', True])
        self.assertTrue(data['transaction'])
        self.assertTrue(len(data['transaction']))
    
    def test_404_add_user_transaction(self):
        res = self.client().get('/users/1', headers=Manager_jwt, json={
            'user_id': 1,
            'type': 'Expense',
            'amount': 55,
            'shop_id': 1
        })
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', False])
    
    def test_422_add_user_transaction(self):
        res = self.client().get('/users/1', headers=Manager_jwt, json={
            'type': 'Splurge',
            'category': 'Luxury item',
            'amount': 100,
            'shop_id': 1
        })
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success', False])
    
    def test_delete_user(self):
        res = self.client().get('/users/1', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['user'])
        self.assertTrue(len(data['user']))
    
    def test_404_delete_user(self):
        res = self.client().get('/users/100', headers=Manager_jwt)
        data = json.loads(res.data.decode('utf-8'))

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success', False])


if __name__ == "__main__":
    unittest.main()
