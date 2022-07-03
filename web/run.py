# from gevent import pywsgi
# import multiprocessing
# from geventwebsocket.handler import WebSocketHandler
# from main import app
import logging
from services.v01.clock.mongoutils import usajobs

log = logging.getLogger()
log.info("hello from run")
usajobs()

# if __name__ == "__main__":
#     log.info("Hello from run main")
#     server = pywsgi.WSGIServer(
#         ("0.0.0.0", 5000), app, handler_class=WebSocketHandler, workers=1 + (multiprocessing.cpu_count() * 2)
#     )
#     server.serve_forever()
