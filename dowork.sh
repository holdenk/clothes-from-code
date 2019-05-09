#!/bin/bash
set -ex
mkdir /tmp/"${DRESS_DIR}"
# Download the file but not too big
(ulimit -f 2024; wget --show-progress "${DRESS_CODE_URL}" -P /tmp/"${DRESS_DIR}"/ --max-redirect 0)
ulimit -f unlimited
INPUT_FILENAME=$(ls -1 /tmp/"${DRESS_DIR}"/)
echo "Generating images"
python gen.py --files /tmp/"${DRESS_DIR}"/"${INPUT_FILENAME}" --out /tmp/"${DRESS_DIR}" --clothing "${CLOTHING_TYPE}"
echo "Starting upload of images"
python cowcow_uploader.py --dress_name "${DRESS_NAME}" --dress_dir /tmp/"${DRESS_DIR}" --clothing "${CLOTHING_TYPE}"
echo "Finished doing work."
