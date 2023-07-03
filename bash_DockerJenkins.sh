#!/bin/bash

echo "Starting Bash of Jenkins Container"

. ./jenkins_config.sh

docker exec -it ${CONTAINER_NAME} /bin/bash

