from flask import jsonify
import traceback
from flask_restful import Resource
import logging
from services.v01.clock.mongoutils import clockTest

log = logging.getLogger("__main__.sub")


class Hello(Resource):
    def get(self):
        try:
            response = clockTest()
            log.info("LOGS!!! Slack response: %s", response)
            # usajobs()
            returnMap = {"message": str(response)}
            return jsonify(returnMap)
        except Exception as err:  # pylint: disable=broad-except
            log.error("unexpectederror %s with trace: %s", err, traceback.format_exc())
            returnMap = {"message": "Unexpected error", "traceback": str(traceback.format_exc())}
            return returnMap, 500
