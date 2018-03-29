#!/bin/bash
cd /app
rethinkdb --bind all --daemon
/usr/bin/python3.6 run.py migrate
/usr/bin/python3.6 run.py runserver --host=0.0.0.0 --port=5000
