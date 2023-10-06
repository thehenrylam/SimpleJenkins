#!/bin/bash

# Define variables
VOLUME_NAME="$1"

BACKUP_SUFFIX=$(echo `date +BACKUP%Y%m%d_%H%M%S`)
BKP_VOLUME_NAME="${VOLUME_NAME}_${BACKUP_SUFFIX}"

# Initialize the docker volume that will be filled up with the reference volume's data
docker volume create --name "$BKP_VOLUME_NAME"

# Copy data from the reference volume and into the backup volume
docker container run --rm \
        -v ${VOLUME_NAME}:/from \
        -v ${BKP_VOLUME_NAME}:/to \
        alpine ash -c "cd /from ; cp -av . /to"

exit 0

