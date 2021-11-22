from flask import make_response
import bcrypt
import os
import jwt
import boto3
from botocore.config import Config
import shutil
from redisconn import conn, dq, lq
from rq import get_current_job
import json
import logging
from bson import ObjectId
import traceback
import gevent
import requests
import requests.exceptions
import copy
import csv
import time
from collections import defaultdict
from datetime import datetime, date
from io import StringIO
from pytz import timezone
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import random
import string

client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

log = logging.getLogger("rq.worker")

def utilsTest():
    return "foo"
