import os
import logging
import traceback
import gevent
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import gspread
from oauth2client.service_account import ServiceAccountCredentials

log = logging.getLogger("rq.worker")

slack_client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

# log.warning('%s', str(os.getenv('GSPREAD_PRIVATE_KEY')))

def create_keyfile_dict():
    variables_keys = {
        "type": "service_account",
        "project_id": os.getenv('GSPREAD_PROJECT_ID'),
        "private_key_id": os.getenv('GSPREAD_PRIVATE_KEY_ID'),
        "private_key": str(os.getenv('GSPREAD_PRIVATE_KEY')).replace('\\n', '\n'),
        "client_email": os.getenv('GSPREAD_CLIENT_EMAIL'),
        "client_id": os.getenv('GSPREAD_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv('GSPREAD_CLIENT_X509_CERT_URL'),
    }
    return variables_keys

creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)

def getGoogleSheet(sheetname):
    try:
        client = gspread.authorize(creds)
        sheet = client.open(sheetname).sheet1
        sheetList = sheet.get_all_values()
        gevent.sleep(2)
    except gspread.exceptions.APIError as e:
        print('gspread error: ', e)
        log.error( "Caught gspread APIError: %s", e )
        log.warning("Sleeping for 10 minutes after error.")
        gevent.sleep(600)
        client = gspread.authorize(creds)
        sheet = client.open(sheetname).sheet1
        sheetList = sheet.get_all_values()
        gevent.sleep(2)
    return client, sheet, sheetList

def utilsTest():
    return "foo"

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

def getExistingJobs(sheetList):
    jobs = []
    for row in range(len(sheetList)):
        if row == 0:
            continue
        jobs.append(sheetList[row][0])
    return jobs

def new_job(job_id, sheetList):
    last_row = len(sheetList)
    new = True
    for row in range(last_row):
        if row == 0:
            continue
        if sheetList[row][0] == job_id:
            new = False
    return new

def write_data(job, sheet, sheetList, channel):
    last_row = len(sheetList)
    job_id = job["id"]
    if job_id == '':
        return 'job_id is empty'
    cell=1
    msg = ""
    log.warning('Writing new job %s, %s to sheets', job['title'], job["id"] )
    for key, field in job.items():
        if key in ['title','job_url']:
            msg += str(field) + '\n'
        sheet.update_cell(last_row, cell, str(field) )
        cell+=1
        gevent.sleep(2)
    log.warning('Writing new job %s, %s to slack', job['title'], job["id"] )
    response = slackAPISendMessage(msg, channel)
    return response
