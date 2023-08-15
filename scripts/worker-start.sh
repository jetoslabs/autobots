#! /usr/bin/env bash
set -e

celery -A autobots.worker.celery worker --loglevel=info # -Q main-queue

