import os
import requests
import requests.exceptions
import logging
from web.services.v01.utils import *
from web.services.v01.clock.utils import *
import datetime
from dateutil import parser

log = logging.getLogger(__name__)

# msg = 'job title'+'\n'
# msg += 'job location'+'\n'
# msg += 'job title'+'\n'
# msg += 'job title'+'\n'
# msg += 'job title'+'\n'
# msg += 'job title'+'\n'
# log.warning('Writing new job %s, %s to slack',
#             'job title', 'job id')
# response = slackAPISendMessage(msg, 'usajobs')
# ts = response['ts']
# log.info('msg ts is: %s', ts)
# reply_msg = 'job duties'
# reply_response = slackAPISendReply(reply_msg, 'usajobs', ts)

# sys.exit()

usajobs()
