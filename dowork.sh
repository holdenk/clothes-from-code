#!/bin/bash
set -ex
mkdir /tmp/"${DRESS_NAME}"
# Download the file but not too big
(ulimit -f 2024; wget --show-progress "${DRESS_CODE_URL}" -P /tmp/"${DRESS_NAME}"/ --max-redirect 0)
INPUT_FILENAME=$(ls -1 /tmp/"${DRESS_NAME}"/)
python gen.py --files /tmp/"${DRESS_NAME}"/"${INPUT_FILENAME}" --out /tmp/"${DRESS_NAME}"
