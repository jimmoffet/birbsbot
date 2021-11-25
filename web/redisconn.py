import redis
import os
from rq import Queue
import logging

log = logging.getLogger(__name__)

if os.environ.get('DEBUG') == 'True':
    redis_url = os.getenv('REDIS_URL_LOCAL')
else:
    redis_url = os.getenv('REDIS_URL')

# redis_url = os.getenv('REDISTOGO_URL')
conn = redis.from_url(redis_url, retry_on_timeout=True, ssl_cert_reqs=None)
lq = Queue('low', connection=conn)
dq = Queue('default', connection=conn)
hq = Queue('high', connection=conn)
chatconn = redis.from_url(redis_url, socket_keepalive=True, retry_on_timeout=True)
