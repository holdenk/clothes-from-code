#!/bin/bash
DRESS_NAME=$1
export DRESS_NAME
DRESS_CODE_URL=$2
export DRESS_CODE_URL
if [ -z "$DRESS_NAME" ]; then
  echo "No dress name specified. leaving"
  exit 0
fi
if [ -z "$DRESS_CODE_URL" ]; then
  echo "No dress source specified. leaving"
  exit 0
fi
./dowork.sh
rm -rf /tmp/"${DRESS_NAME}"
