#!/bin/bash

echo "Opening Logs of Jenkins Container"

. ./jenkins_config.sh

docker logs ${CONTAINER_NAME}

