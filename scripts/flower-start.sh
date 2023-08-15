#! /usr/bin/env bash
set -e

celery -A autobots.worker.celery flower 5555 --loglevel=info
