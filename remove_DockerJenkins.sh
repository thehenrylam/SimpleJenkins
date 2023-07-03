#!/bin/bash

echo "Removing Jenkins Container"

. ./jenkins_config.sh

docker stop ${CONTAINER_NAME}

docker rm ${CONTAINER_NAME}

