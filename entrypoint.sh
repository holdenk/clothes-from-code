#!/bin/bash
cd /usr/src/app/
FLASK_APP=/usr/src/app/server.py flask run --host=0.0.0.0
