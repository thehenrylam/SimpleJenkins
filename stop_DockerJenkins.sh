#!/bin/bash

echo "Stopping Jenkins Container"

. ./jenkins_config.sh

docker stop ${CONTAINER_NAME}

