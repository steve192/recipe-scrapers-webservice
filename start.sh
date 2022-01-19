#!/usr/bin/env sh
uwsgi --http :9090 --wsgi-file src/app.py --uid=www-data --gid=www-data
