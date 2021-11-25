import logging
import sys
import os
import traceback
import gevent
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from services.v01.clock.utils import clockTest, usajobs
from services.v01.utils import utilsTest
from redisconn import lq

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

log = logging.getLogger("rq.worker")

try:
    log.warning('Clock process is awake, running usajobs immediately')
    lq.enqueue(usajobs, ttl=3600, failure_ttl=3600, job_timeout=600)

    sched = BlockingScheduler()
    sched.add_job(usajobs, 'interval', hours=1)
    sched.add_job(clockTest, CronTrigger.from_crontab('0 20 * * 0-6',timezone='UTC'))
    sched.start()

except Exception as err: # pylint: disable=broad-except
    log.error('Clock process failed with error: %s and traceback: %s', err, str(traceback.format_exc()) )
