"""
Network configuration module
============================

Infers configuration from ENV vars when possible
defaults to unsing localhost resources on standard ports

Json format is used for both task and result serialization.

Also declares the timezone to use for checking clock sync in
multicomputer configurations.
"""

import os

env=os.environ

broker_url=None

if env.get('REDIS_URI') and env.get('REDIS_DB'):
    broker_url=env.get('REDIS_URI') + '/' + env.get('REDIS_DB')
else:
    broker_url='redis://localhost:6379/2'

result_backend=None

if env.get('MONGODB_URI') and env.get('EXECUTOR_DB'):
    result_backend=env.get('MONGODB_URI') + '/' + env.get('EXECUTOR_DB')
else:
    result_backend='mongodb://localhost:27017/from_celery'


task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = env.get('TZ') or 'Europe/Amsterdam'
enable_utc = True
