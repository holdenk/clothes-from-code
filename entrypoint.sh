#!/bin/bash
cd /usr/src/app/
MOZ_HEADLESS=1
export MOZ_HEADLESS
FLASK_APP=/usr/src/app/server.py flask run --host=0.0.0.0
