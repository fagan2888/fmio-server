#!/bin/bash
# Startup script for running e.g. in heroku Procfile
celery -A fmio.server:cel worker -B &
gunicorn fmio.server:app
