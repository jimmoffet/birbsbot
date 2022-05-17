import os
import time
import json
import requests
import logging
from dateutil import parser
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from pymongo import MongoClient

USAJOBSKEY = os.environ["USAJOBS_API_KEY"]

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

log = logging.getLogger()

db_client = MongoClient(os.environ["MONGO_URI"], connect=False)
db = db_client.usajobs
jobs = db["jobs"]


def slackAPISendReply(text, channel, ts):
    # api_response = client.api_test()
    # log.info(u'slack api response is %s', api_response)
    response = "unexpected error"
    try:
        response = slack_client.chat_postMessage(channel=channel, text=text, thread_ts=ts)
        log.info("slack api chat response is %s", response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        response = str(e.response)
        log.error("Got an error: %s", e.response["error"])
        log.error("Error response: %s", e.response)
    return response


def slackAPISendMessage(msg, channel):
    # api_response = client.api_test()
    # log.info('slack api response is %s', api_response)
    response = "unexpected error"
    try:
        response = slack_client.chat_postMessage(channel=channel, text=msg)
        # log.info('slack api chat response is %s', response)
    except SlackApiError as e:
        # You will get a SlackApiError if "ok" is False
        response = str(e.response)
        log.error("Got an error: %s", e.response["error"])
        log.error("Error response: %s", e.response)
    return response


def respond(err, code, body=None):
    function_response = {
        "statusCode": "400" if err else "200",
        "body": json.dumps({"error": err}) if err else json.dumps(body),
        "headers": {
            "Content-Type": "application/json",
        },
    }
    # log.info('Response: %s', function_response)
    # print(function_response)
    return function_response


def lambda_handler(event, context):
    err = None
    body = None

    # parsed = json.loads(event)

    log.warning("event is: %s", event)

    base = "https://data.usajobs.gov/api/"
    endpoint = "search?ResultsPerPage=500&"

    search_phrase = event["search_phrase"]
    grade = event["grade"]

    # search_phrase = 'chief innovation'
    # grade = 16

    title_excludes = [
        "INFOSEC",
        "CYBERSECURITY",
        "SECURITY",
        "Physician",
        "Surgeon",
        "Podiatrist",
        "Radiologist",
        "SYSADMIN",
        "Systems Admin",
        "System Admin",
        "Systems Engineer",
        "doctoral",
        "marketing",
        "not eligible for permanent remote",
        "not eligible for remote",
        "not a virtual",
        "electronics engineer",
        "sharepoint",
        "oracle",
        "business intelligence",
        "signal",
        "professor",
        "general engineer",
        "civil engineer",
        "Physicist",
        "aerospace",
        "accountant",
        "network",
        "nurse",
    ]

    grade = 16

    search_param = "Keyword=" + search_phrase + "&"
    hiring_path_param = "HiringPath=public&HiringPath=fed-excepted"
    grade_param = "PayGradeLow=" + str(grade) + "&"
    params = (
        search_param
        + hiring_path_param
        + grade_param
        + "gs=true&RemunerationMinimumAmount=170533&RemunerationMaximumAmount=500000"
    )

    url = base + endpoint + params

    headers = {
        "User-Agent": "jimmoffet@gmail.com",
        "Authorization-Key": os.getenv("USAJOBS_API_KEY"),
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:

        # log.warning("%s", response.status_code)

        json_data = response.json()
        body = json_data

        # result_dict = json_data['SearchResult']
        result_count = json_data["SearchResult"]["SearchResultCount"]
        log.warning("result_count: %s", result_count)
        result_count_all = json_data["SearchResult"]["SearchResultCountAll"]
        log.warning("result_count_all: %s", result_count_all)

        result_array = json_data["SearchResult"]["SearchResultItems"]

        new_ids = []
        for posting in result_array:
            try:
                job_id = posting["MatchedObjectId"]
                new_ids.append(job_id)
            except:
                pass
        existing_job_objs = jobs.find({"job_id": {"$in": new_ids}})
        existing_job_ids = [str(job["job_id"]) for job in existing_job_objs]
        log.warning("existing_job_ids: %s", existing_job_ids)
        # check in loop and continue if found

        row = 1
        for posting in result_array:
            skip = False
            job_id = "failed to retrieve job id"
            job_employer = "failed to retrieve job employer"
            job_title = "failed to retrieve job title"
            job_location = "failed to retrieve job location"
            job_duties = ""
            job_qualifications = "failed to retrieve job qualifications"
            job_description = "failed to retrieve job description"
            job_url = "failed to retrieve job url"
            job_apply_url = "failed to retrieve job apply url"
            job_close_date = "failed to retrieve job close date"
            job_salary = "failed to retrieve job salary"

            try:
                job_id = posting["MatchedObjectId"]
            except:
                pass

            if job_id in existing_job_ids:
                log.warning("Search: %s, skipping existing job id: %s", search_phrase, job_id)
                continue

            try:
                job_employer = posting["MatchedObjectDescriptor"]["DepartmentName"]
            except:
                pass

            try:
                job_employer += ", " + posting["MatchedObjectDescriptor"]["OrganizationName"]
            except:
                pass

            try:
                job_salary = (
                    "$"
                    + posting["MatchedObjectDescriptor"]["PositionRemuneration"][0]["MinimumRange"]
                    + " to $"
                    + posting["MatchedObjectDescriptor"]["PositionRemuneration"][0]["MaximumRange"]
                )

                min_salary = float(posting["MatchedObjectDescriptor"]["PositionRemuneration"][0]["MinimumRange"])
                max_salary = float(posting["MatchedObjectDescriptor"]["PositionRemuneration"][0]["MaximumRange"])
            except:
                if (
                    "MatchedObjectDescriptor" in posting
                    and "PositionRemuneration" in posting["MatchedObjectDescriptor"]
                    and posting["MatchedObjectDescriptor"]["PositionRemuneration"]
                ):
                    log.error(
                        "Failed to write salary, PositionRemuneration is: %s",
                        posting["MatchedObjectDescriptor"]["PositionRemuneration"][0],
                    )
                pass

            try:
                job_title = posting["MatchedObjectDescriptor"]["PositionTitle"]
            except:
                pass

            for exclude in title_excludes:
                if exclude.lower() in job_title.lower():
                    log.warning("skipping excluded job: %s, job id: %s", job_title, job_id)
                    skip = True
                    break
            if skip:
                continue

            try:
                job_location = posting["MatchedObjectDescriptor"]["PositionLocationDisplay"]
            except:
                pass

            try:
                major_duties = posting["MatchedObjectDescriptor"]["UserArea"]["Details"]["MajorDuties"]
                for item in major_duties:
                    job_duties += item + "\n"
            except:
                pass

            try:
                low_grade = posting["MatchedObjectDescriptor"]["UserArea"]["Details"]["LowGrade"]
            except:
                pass

            try:
                high_grade = posting["MatchedObjectDescriptor"]["UserArea"]["Details"]["HighGrade"]
            except:
                pass

            try:
                job_qualifications = posting["MatchedObjectDescriptor"]["QualificationSummary"]
            except:
                pass

            try:
                job_description = posting["MatchedObjectDescriptor"]["UserArea"]["Details"]["JobSummary"]
            except:
                pass

            try:
                job_url = posting["MatchedObjectDescriptor"]["PositionURI"]
            except:
                pass

            try:
                job_apply_url = posting["MatchedObjectDescriptor"]["ApplyURI"][0]
            except:
                pass

            try:
                job_close_date = posting["MatchedObjectDescriptor"]["ApplicationCloseDate"]
                job_close_date = parser.parse(job_close_date).strftime("%B %d, %Y")
            except:
                pass

            job = {
                "job_id": job_id,
                "title": job_title,
                "location": job_location,
                "duties": job_duties,
                "qualifications": job_qualifications,
                "description": job_description,
                "job_url": job_url,
                "apply_url": job_apply_url,
                "close_date": job_close_date,
                "employer": job_employer,
                "high_grade": high_grade,
                "salary": job_salary,
                "min_salary": min_salary,
                "max_salary": max_salary,
            }

            result = jobs.update_one({"job_id": job_id}, {"$set": job}, upsert=True)
            log.warning(
                "Attempted update, matched_count: %s, modified_count: %s", result.matched_count, result.modified_count
            )

            msg = job_title + "\n"
            msg += "Search: " + search_phrase + "\n"
            msg += job_location + "\n"
            msg += job_employer + "\n"
            msg += job_salary + "\n"
            msg += job_close_date + "\n"
            msg += job_url + "\n"
            log.warning("Writing new job %s, %s to slack", job_title, job_id)
            response = slackAPISendMessage(msg, "usajobs")
            ts = response["ts"]
            # log.info('msg ts is: %s', ts)
            reply_msg = job["duties"]
            reply_response = slackAPISendReply(reply_msg, "usajobs", ts)

        # log.warning("%s", response.status_code)
    else:

        log.error(
            "Request to slack returned an error, status code %s, with text: %s", response.status_code, response.text
        )
        err = response.text

    return respond(err, response.status_code, body)


# lambda_handler(None, None)
