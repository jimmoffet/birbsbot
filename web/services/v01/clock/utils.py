import os
import logging
from services.v01.utils import *

log = logging.getLogger("rq.worker")

def clockTest():
    log.warning('RUNNING CLOCKTEST')
    response = slackAPISendMessage("test message", '#new-nest')
    log.warning('slack api response is %s', response)
    return response

def usajobs():
    _, sheet, sheetList = getGoogleSheet('usajobs')
    existing_jobs = getExistingJobs(sheetList)

    base = 'https://data.usajobs.gov/api/'
    endpoint = 'search?ResultsPerPage=500&'

    search_phrases = [
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
        ('devsecops', 13),
        ('python', 13),
        ('"location negotiable"', 13),
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

            log.warning("%s",response.status_code)

            json_data = response.json()

            # result_dict = json_data['SearchResult']
            result_count = json_data['SearchResult']['SearchResultCount']
            log.warning("%s",result_count)
            result_count_all = json_data['SearchResult']['SearchResultCountAll']
            log.warning("%s",result_count_all)

            result_array = json_data['SearchResult']['SearchResultItems']

            row=1
            for posting in result_array:
                skip = False
                job_id = 'failed to retrieve job id'
                job_title = 'failed to retrieve job title'
                job_location = 'failed to retrieve job location'
                job_duties = ''
                job_qualifications = 'failed to retrieve job qualifications'
                job_description = 'failed to retrieve job description'
                job_url = 'failed to retrieve job url'
                job_apply_url = 'failed to retrieve job apply url'

                try:
                    job_id = posting['MatchedObjectId']
                except:
                    pass

                try:
                    job_title = posting['MatchedObjectDescriptor']['PositionTitle']
                except:
                    pass
                
                for exclude in title_excludes:
                    if exclude.lower() in job_title.lower():
                        log.warning('skipping excluded job: %s', job_title)
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

                job = {
                    'id': job_id,
                    'title': job_title,
                    'location': job_location,
                    'duties': job_duties,
                    'qualifications': job_qualifications,
                    'description': job_description,
                    'job_url': job_url,
                    'apply_url': job_apply_url
                }

                if job_id in existing_jobs:
                    log.warning('skipping existing job: %s', job_title)
                    continue
                
                _, sheet, sheetList = getGoogleSheet('usajobs')
                existing_jobs = getExistingJobs(sheetList)

                if job_id in existing_jobs:
                    log.warning('skipping existing job: %s', job_title)
                    continue
                
                existing_jobs.append(job_id)
                resp = write_data(job, sheet, sheetList, 'usajobs')
        except Exception as e:
            log.error('usajobs error: %s for search phrase: %s', e, search_phrase)
            gevent.sleep(2)
            continue
