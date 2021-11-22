import os
import time
import logging
import sys, traceback
# uncomment for local testing (no docker env)
# from dotenv import load_dotenv
# load_dotenv()
# uncomment for local testing (no docker env)
from rq import Worker, Queue, Connection
from redisconn import conn
from exception_handlers import job_error_handler
import gevent


log = logging.getLogger(__name__)
# log.setLevel('INFO')

logging_level = "INFO"

if os.environ.get('DEBUG') == 'True':
    log.setLevel('INFO')
    logging_level = "INFO"
elif os.environ.get('DB_REMOTE') == 'STAGING':
    log.setLevel('WARNING')
    logging_level = "WARNING"
else:
    log.setLevel('WARNING')
    logging_level = "WARNING"

def run():
    then = time.time()
    try:
        workers = Worker.all(connection=conn)
        for worker in workers:
            job = worker.get_current_job()
            log.info('WORKERS ALREADY EXIST %s', "" )
            if job is not None:
                id = str( job.get_id() )
                log.info('Dead? worker, requeuing job: %s', id )
                job.ended_at = time.time()
                oldmeta = job.meta
                job.meta['old_meta'] = oldmeta
                job.meta['queued'] = True
                job.save_meta()
                #worker.failed_queue.quarantine(job, exc_info=("Dead worker", "Moving job to failed queue"))
                job.status = "queued"
                log.info('job status is now: %s', job.status )
            worker.register_death()
    except Exception as err:
        log.error('worker unexpectederror %s with trace: %s', err, traceback.format_exc() )
        gevent.sleep(5)
        ### TODO this should be a retry loop with a slack failure message if retries exceeded
        workers = Worker.all(connection=conn)
        for worker in workers:
            job = worker.get_current_job()
            log.info('WORKERS ALREADY EXIST %s', "" )
            if job is not None:
                id = str( job.get_id() )
                log.info('Dead? worker, requeuing job: %s', id )
                job.ended_at = time.time()
                oldmeta = job.meta
                job.meta['old_meta'] = oldmeta
                job.meta['queued'] = True
                job.save_meta()
                #worker.failed_queue.quarantine(job, exc_info=("Dead worker", "Moving job to failed queue"))
                job.status = "queued"
                log.info('job status is now: %s', job.status )
            worker.register_death()

    # log.info('Booting worker, time is: {}'.format( then ))
    log.warning('Booting worker, time is: %s', then )
    listen = ['high','default','low']

    while True:
        try:
            with Connection(conn):
                worker = Worker(map(Queue, listen), log_job_description=False, exception_handlers=[job_error_handler], disable_default_exception_handler=True)
                worker.work(with_scheduler=True, logging_level=logging_level)
        # except redis.ConnectionError:
        #     #traceback.print_exc()
        #     time.sleep(.01)
        except Exception as e:
            log.warning('Worker rebooting on error: %s with traceback: %s', str(e), str(traceback.format_exc()) )
            # traceback.print_exc()

if __name__ == '__main__':
    run()
