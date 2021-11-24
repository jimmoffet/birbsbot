from flask import json, jsonify
import os
import tempfile
import pytest
from main import app
from db import users
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity)
import logging

log = logging.getLogger(__name__)

############################
# {
# 	"username": "travisuser",
# 	"password": "travispassword"
# }
############################

# @pytest.fixture(scope='function')
# def client():
#     db_fd, app.config['DATABASE'] = tempfile.mkstemp()
#     # create a new mongo instance for testing?
#     app.config['TESTING'] = True
#     app.config['JWT_HEADER_TYPE'] = 'Bearer'
#     app.config['JWT_BLACKLIST_ENABLED'] = False

#     with app.test_client() as client:
#         yield client
#     os.close(db_fd)
#     os.unlink(app.config['DATABASE'])

# def test_root(client):
#     rv = client.get('/', follow_redirects=True)
#     assert b'Hello' in rv.data

# def test_register(client):
#     rv = client.post('/register', json={
#         'email': 'newuser@email.com',
#         'handle': 'newuser',
#         'password': 'password'
#     })
#     json_data = rv.get_json()
#     log.info('json response is %s', json_data )
#     assert 'successfully' in json_data['message']

# def test_auth(client):
#     rv = client.post('/auth', json={
#         'emailhandle': 'newuser@email.com',
#         'password': 'password'
#     })
#     json_data = rv.get_json()
#     assert 'access_token' in json_data
#     assert 'SUCCESS' in json_data['message']

# def test_feed(client):
#     with app.test_request_context():
#         access_token = create_access_token(identity='testuser')
#     headers = {'Authorization': 'Bearer {}'.format(access_token)}
#     rv = client.get('/feed', headers=headers)
#     json_data = rv.get_json()
#     print(json_data)
#     assert 'SUCCESS' in json_data['message']
#     assert 'https' in json_data['videos'][0]["playlist"]
