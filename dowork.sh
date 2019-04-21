#!/bin/bash
set -ex
mkdir /tmp/${DRESS_NAME}
wget ${DRESS_CODE_URL} -o /tmp/${DRESS_NAME}/
