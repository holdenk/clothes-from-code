#!/bin/bash
CLOTHING_TYPE=$1
export CLOTHING_TYPE
DRESS_DIR=$2
export DRESS_DIR
DRESS_NAME=$3
export DRESS_NAME
DRESS_CODE_URL=$4
export DRESS_CODE_URL
if [ -z "$DRESS_NAME" ]; then
  echo "No dress name specified. leaving"
  exit 0
fi
if [ -z "$DRESS_CODE_URL" ]; then
  echo "No dress source specified. leaving"
  exit 0
fi
echo "Generating the dress"
unbuffer ./dowork.sh || echo "Failed to generate the dress"
echo "Cleaning up"
rm -rf /tmp/"${DRESS_DIR}"
