#!/bin/bash
celery -A sim.executor.tasks worker --loglevel=info -E --concurrency=4
