import os
import logging
import traceback
import gevent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

log = logging.getLogger("rq.worker")

slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))


def slackAPISendMessage(msg, channel):
    # api_response = client.api_test()
    # log.info('slack api response is %s', api_response)
    response = 'unexpected error'
    try:
        response = slack_client.chat_postMessage(channel=channel, text=msg)
        # log.info('slack api chat response is %s', response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        response = str(e.response)
        log.error("Got an error: %s", e.response['error'])
        log.error("Error response: %s", e.response)
    return response


def slackAPISendReply(text, channel, ts):
    # api_response = client.api_test()
    # log.info(u'slack api response is %s', api_response)
    response = 'unexpected error'
    try:
        response = slack_client.chat_postMessage(
            channel=channel, text=text, thread_ts=ts)
        log.info(u'slack api chat response is %s', response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        response = str(e.response)
        log.error("Got an error: %s", e.response['error'])
        log.error("Error response: %s", e.response)
    return response
