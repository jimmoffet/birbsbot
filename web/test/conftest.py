import logging
from flask import json, jsonify

# uncomment for local testing (no docker env)
# from dotenv import load_dotenv
# load_dotenv('.testenv')
# uncomment for local testing (no docker env)



import pytest
from main import app

@pytest.fixture(scope='session')
def client():
    app.config['TESTING'] = True
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_BLACKLIST_ENABLED'] = False
    with app.test_client() as client:
        yield client
    # teardown
    print("tearing down..")


# @pytest.fixture(scope='session')
# def get_headers():
#     with app.test_client() as client:
#         response = client.post(
#             '/v0.1/auth', json={'emailhandle': 'testing@email.com', "password": "password"})
#         json_data = response.get_json()

#         headers = {"Content-Type": "application/json",
#                    "Authorization": "Bearer {}".format(json_data['access_token'])}
#         return headers
