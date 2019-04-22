#!/bin/bash
cd /usr/src/app/
MOZ_HEADLESS=1
export MOZ_HEADLESS
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 800 server:app
unset MOZ_HEADLESS
