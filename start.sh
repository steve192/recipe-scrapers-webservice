#!/usr/bin/env sh
gunicorn -b 0.0.0.0:9090 --threads 1 --preload --workers 1 src.app:app
#uwsgi --http :9090 --wsgi-file src/app.py --uid=www-data --gid=www-data
