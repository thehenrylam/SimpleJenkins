#!/bin/bash

echo "Start Jenkins Container"

. ./jenkins_config.sh

docker start ${CONTAINER_NAME}

