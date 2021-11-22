import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))

log = logging.getLogger("rq.worker")

def job_error_handler(job, exc_type, exc_value, traceback):

    env = os.environ.get('DB_REMOTE')

    log.info("===>>>> job_error_handler START")

    send_to_slack_string = env + ": " + str(
        job.get_id()) + "\n" + "exc_type: " + exc_type + " exc_value: " + exc_value + "\n" + "traceback: " + traceback

    try:
        response = client.chat_postMessage(channel="#redis-queue-failures", text=send_to_slack_string)
    except SlackApiError as e:
        response = str(e.response)
        log.error(f"job_error_handler Got an error: {e.response['error']}")
        log.error(f"job_error_handler Error response: {e.response}")
    return response

## TODO - Not in use
def error_handler(exc_type, exc_value, traceback):

    env = os.environ.get('DB_REMOTE')

    log.info("===>>>> error_handler START")

    send_to_slack_string = env + ": " + "exc_type: " + exc_type + " exc_value: " + exc_value + "\n" + "traceback: " + traceback

    try:
        response = client.chat_postMessage(channel="#redis-queue-failures", text=send_to_slack_string)
    except SlackApiError as e:
        response = str(e.response)
        log.error(f"error_handler Got an error: {e.response['error']}")
        log.error(f"error_handler Error response: {e.response}")
    return response
