#!/bin/bash
if [ -z "$DRESS_NAME" ]; then
  echo "No dress name specified. leaving"
  exit 0
fi
./dowork.sh
rm -rf /tmp/${DRESS_NAME}
