from gevent import pywsgi
import multiprocessing
from geventwebsocket.handler import WebSocketHandler
from main import app

if __name__ == "__main__":
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app, handler_class=WebSocketHandler, workers=1+(multiprocessing.cpu_count()*2) )
    server.serve_forever()
