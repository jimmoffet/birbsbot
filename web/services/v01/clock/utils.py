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
    client, sheet, sheetList = getGoogleSheet('usajobs')

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
        ('"slog.warning"', 13),
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

    title_excludes = ['INFOSEC', 'CYBERSECURITY', 'SECURITY']

    for search_phrase, grade in search_phrases:
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
            
            job_title = posting['MatchedObjectDescriptor']['PositionTitle']
            
            for exclude in title_excludes:
                if exclude in job_title:
                    log.warning('skipping excluded job: %s', job_title)
                    skip = True
                    break
            if skip:
                continue

            # log.warning(job_title, posting['MatchedObjectDescriptor']['PositionLocationDisplay'])
            # log.warning(posting['MatchedObjectDescriptor']['PositionLocation'])
            # log.warning(posting['MatchedObjectDescriptor']['UserArea']['Details']['JobSummary'] )
            duties = ''
            for item in posting['MatchedObjectDescriptor']['UserArea']['Details']['MajorDuties']:
                duties += item+'\n'
            # log.warning(duties)
            # log.warning(posting['MatchedObjectDescriptor']['QualificationSummary'])

            apply_url = ''
            if 'ApplyURI' in posting['MatchedObjectDescriptor'] and posting['MatchedObjectDescriptor']['ApplyURI']:
                apply_url = posting['MatchedObjectDescriptor']['ApplyURI'][0]

            job = {
                'id': posting["MatchedObjectId"],
                'title': posting['MatchedObjectDescriptor']['PositionTitle'],
                'location': posting['MatchedObjectDescriptor']['PositionLocationDisplay'],
                'duties': duties,
                'qualifications': posting['MatchedObjectDescriptor']['QualificationSummary'],
                'description': posting['MatchedObjectDescriptor']['UserArea']['Details']['JobSummary'],
                'job_url': posting['MatchedObjectDescriptor']["PositionURI"],
                'apply_url': apply_url
            }
            
            resp = write_data(job, sheet, sheetList, 'usajobs', row)
            row+=1
            # break
            # log.warning(str(resp))
