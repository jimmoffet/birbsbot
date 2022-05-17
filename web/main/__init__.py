import logging
import os
import datetime
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_sockets import Sockets

### redis connection pools
# from redisconn import conn, dq, chatconn
### custom json encoder for mongo objects
from customjsonencoder import CustomJSONEncoder

##############################
#### Build and config app ####
##############################

app = Flask(__name__)
api = Api(app)
sockets = Sockets(app)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["JWT_SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=60)
app.config["JWT_BLACKLIST_ENABLED"] = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access", "refresh"]
app.config["PROPAGATE_EXCEPTIONS"] = True
app.json_encoder = CustomJSONEncoder
app.config["RESTFUL_JSON"] = {"cls": CustomJSONEncoder}
jwt = JWTManager(app)

if os.getenv("DEBUG") == "True":
    app.debug = True

# @jwt.token_in_blacklist_loader
# def check_if_token_in_blacklist(decrypted_token):
#     jti = decrypted_token['jti']
#     token_in_redis = conn.get(jti)
#     return token_in_redis is not None

##############################
########## Logging ###########
##############################

if os.environ.get("DEBUG") == "True":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

log = logging.getLogger()
log.info("Hello from init.py")

##############################
########## Routes ############
##############################

# from routes import *

### http:// routes
import routes.hello  # root

### ws:// routes
import routes.echo  # websocket test echo

##############################
######### Endpoints ##########
##############################

### api endpoints by version
from services.v01.endpoints import *
