import logging
from pymongo import MongoClient, TEXT
import os

# docker builds the db directory into a mongo instance, we connect to it below
db_client = None
if os.environ.get('DB_REMOTE') == 'PROD':
    db_client = MongoClient(os.environ.get(
        'MONGO_URI'), connect=False)
    db = db_client.usajobs
    oplog_db = db_client.local
    admin_db = db_client.admin
    oplog = oplog_db.oplog.rs

jobs = db["jobs"]
