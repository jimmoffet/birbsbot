import os
import sys
import traceback
import requests
import logging
from services.v01.utils import *
from dateutil import parser

log = logging.getLogger("rq.worker")


def clockTest():
    log.warning('RUNNING CLOCKTEST')
    response = slackAPISendMessage("test message", '#new-nest')
    log.warning('slack api response is %s', response)
    return response


def usajobs():
    _, sheet, sheetList = getGoogleSheet('usajobs')
    existing_jobs_array = getExistingJobs(sheetList)
    existing_jobs = set(existing_jobs_array)

    base = 'https://data.usajobs.gov/api/'
    endpoint = 'search?ResultsPerPage=500&'

    search_phrases = [
        ('"computer engineer"', 14),
        ('"computer scientist"', 14),
        ('"software engineer"', 14),
        ('"software engineering"', 13),
        ('"software developer"', 14),
        ('"software quality"', 13),
        ('"technology product"', 13),
        ('"software product"', 13),
        ('devsecops', 13),
        ('"location negotiable"', 13),
        ('iaas', 14),
        ('"amazon web"', 14),
        ('javascript', 14),
        ('"full stack"', 14),
        ('"back end"', 14),
        ('"backend"', 14),
        ('"user centered"', 13),
        ('"human centered design"', 13),
        ('"user research"', 13),
        ('product "roadmap"', 13),
        ('"product manager"', 13),
        ('"product management"', 13),
        ('"product development"', 13),
        ('"digital services"', 13),
        ('"software development"', 14),
        ('"user stories"', 13),
        ('"sprint"', 13),
        ('"scrum"', 13),
        ('"product strategy"', 13),
        ('"software life cycle"', 14),
        ('agile software', 14),
        ('github', 14),
        ('appsw', 14),
        ('devops', 13),
        ('python', 13),
    ]

    title_excludes = [
        'INFOSEC',
        'CYBERSECURITY',
        'SECURITY',
        'Physician',
        'SYSADMIN',
        'Systems Admin',
        'System Admin',
        'Systems Engineer',
        'doctoral',
        'marketing',
        'not eligible for permanent remote',
        'not eligible for remote',
        'not a virtual',
        'electronics engineer',
        'sharepoint',
        'oracle',
        'business intelligence',
        'signal',
        'professor',
        'general engineer',
        'civil engineer',
        'Physicist',
        'aerospace',
        'accountant',
        'network',
        'nurse'
    ]

    for search_phrase, grade in search_phrases:
        try:
            search_param = 'Keyword=' + search_phrase + '&'
            hiring_path_param = 'HiringPath=public&'
            grade_param = 'PayGradeLow=' + str(grade) + '&'
            params = search_param + hiring_path_param + grade_param

            url = base + endpoint + params

            headers = {
                'User-Agent': 'jimmoffet@gmail.com',
                'Authorization-Key': os.getenv('USAJOBS_API_KEY'),
            }

            response = requests.get(url, headers=headers)

            # log.warning("%s", response.status_code)

            json_data = response.json()

            # result_dict = json_data['SearchResult']
            result_count = json_data['SearchResult']['SearchResultCount']
            # log.warning("%s", result_count)
            result_count_all = json_data['SearchResult']['SearchResultCountAll']
            # log.warning("%s", result_count_all)

            result_array = json_data['SearchResult']['SearchResultItems']

            row = 1
            for posting in result_array:
                skip = False
                job_id = 'failed to retrieve job id'
                job_employer = 'failed to retrieve job employer'
                job_title = 'failed to retrieve job title'
                job_location = 'failed to retrieve job location'
                job_duties = ''
                job_qualifications = 'failed to retrieve job qualifications'
                job_description = 'failed to retrieve job description'
                job_url = 'failed to retrieve job url'
                job_apply_url = 'failed to retrieve job apply url'
                job_close_date = 'failed to retrieve job close date'
                job_salary = 'failed to retrieve job salary'

                try:
                    job_id = posting['MatchedObjectId']
                except:
                    pass

                if job_id in existing_jobs:
                    log.warning('Search: %s, skipping existing job id: %s',
                                search_phrase, job_id)
                    continue

                try:
                    job_employer = posting['MatchedObjectDescriptor']['DepartmentName']
                except:
                    pass

                try:
                    job_employer += ', ' + \
                        posting['MatchedObjectDescriptor']['OrganizationName']
                except:
                    pass

                try:
                    job_salary = '$' + posting['MatchedObjectDescriptor']['PositionRemuneration'][0]['MinimumRange'] + \
                        ' to $' + \
                        posting['MatchedObjectDescriptor']['PositionRemuneration'][0]['MaximumRange']
                except:
                    if 'MatchedObjectDescriptor' in posting and 'PositionRemuneration' in posting['MatchedObjectDescriptor'] and posting['MatchedObjectDescriptor']['PositionRemuneration']:
                        log.error('Failed to write salary, PositionRemuneration is: %s',
                                  posting['MatchedObjectDescriptor']['PositionRemuneration'][0])
                    pass

                try:
                    job_title = posting['MatchedObjectDescriptor']['PositionTitle']
                except:
                    pass

                for exclude in title_excludes:
                    if exclude.lower() in job_title.lower():
                        log.warning(
                            'skipping excluded job: %s, job id: %s', job_title, job_id)
                        skip = True
                        break
                if skip:
                    continue

                try:
                    job_location = posting['MatchedObjectDescriptor']['PositionLocationDisplay']
                except:
                    pass

                try:
                    major_duties = posting['MatchedObjectDescriptor']['UserArea']['Details']['MajorDuties']
                    for item in major_duties:
                        job_duties += item+'\n'
                except:
                    pass

                try:
                    job_qualifications = posting['MatchedObjectDescriptor']['QualificationSummary']
                except:
                    pass

                try:
                    job_description = posting['MatchedObjectDescriptor']['UserArea']['Details']['JobSummary']
                except:
                    pass

                try:
                    job_url = posting['MatchedObjectDescriptor']["PositionURI"]
                except:
                    pass

                try:
                    job_apply_url = posting['MatchedObjectDescriptor']['ApplyURI'][0]
                except:
                    pass

                try:
                    job_close_date = posting['MatchedObjectDescriptor']['ApplicationCloseDate']
                    job_close_date = parser.parse(
                        job_close_date).strftime("%B %d, %Y")
                except:
                    pass

                job = {
                    'id': job_id,
                    'title': job_title,
                    'location': job_location,
                    'duties': job_duties,
                    'qualifications': job_qualifications,
                    'description': job_description,
                    'job_url': job_url,
                    'apply_url': job_apply_url,
                    'close_date': job_close_date,
                    'employer': job_employer,
                    'salary': job_salary
                }

                _, sheet, sheetList = getGoogleSheet('usajobs')
                existing_jobs_array = getExistingJobs(sheetList)
                existing_jobs_set = set(existing_jobs_array)
                existing_jobs.union(existing_jobs_set)

                if job_id in existing_jobs:
                    log.warning('Search: %s, skipping existing job: %s, job id: %s',
                                search_phrase, job_title, job_id)
                    continue

                existing_jobs.add(job_id)
                resp = write_datas(job, sheet, sheetList, 'usajobs')

                msg = job['title']+'\n'
                msg += 'Search: ' + search_phrase + '\n'
                msg += job['location']+'\n'
                msg += job_employer+'\n'
                msg += job_salary+'\n'
                msg += job['close_date']+'\n'
                msg += job['job_url']+'\n'
                log.warning('Writing new job %s, %s to slack',
                            job['title'], job_id)
                response = slackAPISendMessage(msg, 'usajobs')
                ts = response['ts']
                # log.info('msg ts is: %s', ts)
                reply_msg = job['duties']
                reply_response = slackAPISendReply(reply_msg, 'usajobs', ts)

        except Exception as e:
            log.error('usajobs error: %s for search phrase: %s, with traceback: %s',
                      e, search_phrase, traceback.format_exc())
            gevent.sleep(2)
            continue
