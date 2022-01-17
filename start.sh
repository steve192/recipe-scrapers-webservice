#!/usr/bin/env sh
service nginx start
uwsgi --http :9090 --wsgi-file src/app.py --uid=www-data --gid=www-data
