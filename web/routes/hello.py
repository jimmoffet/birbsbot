from flask import jsonify, request
from main import app
import logging
from bson.objectid import ObjectId
from lambdas.BirbsBotHello import lambda_handler

log = logging.getLogger("__main__.sub")


@app.route("/hello", methods=["GET"])
def helloworld():
    param = None
    if request.args.get("param"):
        param = request.args.get("param")
        log.info("param is: %s", param)
    ret_str = "Hello World!"
    return ret_str


@app.route("/")
def helloworldroot():
    resp = "Hello World!"
    log.info("Serving root, Hello World!")
    # raw_response = lambda_handler(None, None)
    # resp = raw_response.body
    return resp
