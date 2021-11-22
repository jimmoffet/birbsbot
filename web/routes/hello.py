from flask import jsonify, request
from main import app
from redisconn import conn, dq
import logging
from bson.objectid import ObjectId

log = logging.getLogger(__name__)

@app.route('/hello')
def helloworld():

    param = None
    if request.args.get('param'):
        param = request.args.get('param')
        log.info('param is: %s', param )

    ret_str = "Hello World!"
    return ret_str

@app.route('/')
def helloworldroot():
    ret_str = "Hello World!"
    return ret_str
