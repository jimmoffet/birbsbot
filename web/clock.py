import logging
import sys
import os
import traceback
import gevent
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from services.v01.clock.utils import clockTest
from services.v01.utils import utilsTest
# from redisconn import lq

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

log = logging.getLogger("rq.worker")

try:
    if os.environ.get('DEBUG') != 'True':
        sched = BlockingScheduler()

        if os.getenv('DB_REMOTE') == 'STAGING' or os.getenv('DB_REMOTE') == 'PROD':
            sched.add_job(clockTest, 'interval', hours=1)
            sched.add_job(utilsTest, CronTrigger.from_crontab('0 20 * * 0-6',timezone='UTC'))

        sched.start()
    else:
        while True:
            gevent.sleep(10)

except Exception as err: # pylint: disable=broad-except
    log.error('Clock process failed with error: %s and traceback: %s', err, str(traceback.format_exc()) )
