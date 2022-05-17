import json
import requests
import os
import logging
from urllib.parse import parse_qs

# WEBHOOK = os.environ['generalWebhook']

log = logging.getLogger()


def respond(err, code, body=None):
    function_response = {
        "statusCode": "400" if err else "200",
        "body": json.dumps({"error": err}) if err else json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    log.info("Response: %s", function_response)
    print(function_response)
    return function_response


def lambda_handler(event, context):
    err = None
    body = None
    # payload = {"text": "Hello, World!"}
    # resp = requests.post(WEBHOOK, json.dumps(payload))
    # if resp.status_code != 200:
    #     log.error('Request to slack returned an error, status code %s, with text: %s',
    #               resp.status_code, resp.text)
    #     err = resp.text
    # else:
    #     body = resp.text
    #     # body = resp.json()

    body = {"text": "Hello, World!"}
    status_code = 200

    return respond(err, status_code, body)


# lambda_handler(None, None)
