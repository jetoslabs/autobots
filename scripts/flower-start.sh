#! /usr/bin/env bash
set -e

celery -b redis://localhost:6379/0 flower 5555 --loglevel=info
