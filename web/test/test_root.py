from flask import json, jsonify
import logging
import pytest


@pytest.mark.run(order=1)
def test_root(client):
    rv = client.get('/v0.1/hello', follow_redirects=True)
    assert b'message' in rv.data
