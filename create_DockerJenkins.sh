#!/bin/bash

echo "Creating Jenkins Container"

. ./jenkins_config.sh

docker build -t ${IMAGE_NAME} .

docker create --name ${CONTAINER_NAME} \
  --restart=on-failure \
  -p 8080:8080 -p 50000:50000 \
  -v ${VOLUME_NAME}:/var/jenkins_home \
  ${IMAGE_NAME}

