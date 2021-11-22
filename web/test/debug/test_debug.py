from flask import json, jsonify
import logging
import pytest

@pytest.mark.run(order=0)
def test_auth(client):
    response = client.get("/v0.1/hello", follow_redirects=True)
    json_data = response.get_json()
    print("THIS IS THE RESPONSE FOR TEST AUTH", json_data)
    assert 'foo' in json_data['message']
