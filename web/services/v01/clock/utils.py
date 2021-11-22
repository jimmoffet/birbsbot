import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
# from flask import make_response
# from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_refresh_token_required, get_jwt_identity, decode_token)
# from botocore.config import Config
# from redisconn import conn, dq
# from rq.decorators import job
# from rq import get_current_job
# import json
# from bson import ObjectId
# import traceback
# import gevent
# import requests.exceptions

log = logging.getLogger("rq.worker")

slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

def slackAPISendMessage(msg, channel):
    # api_response = client.api_test()
    # log.info('slack api response is %s', api_response)
    response = 'unexpected error'
    try:
        response = slack_client.chat_postMessage(channel=channel, text=msg)
        log.info('slack api chat response is %s', response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        response = str(e.response)
        log.error("Got an error: %s", e.response['error'])
        log.error("Error response: %s", e.response)
    return response

def clockTest():
    response = slackAPISendMessage("test message", '#new-nest')
    return response
