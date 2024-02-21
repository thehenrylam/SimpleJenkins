#!/bin/bash

CURR_SCRIPT_FILEPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_BASE_DIR="$(cd "${CURR_SCRIPT_FILEPATH}/.." && pwd)"

AUTHENTICATION_FILE=$1

${SCRIPT_BASE_DIR}/jenkins/jenkins-cli.sh ${AUTHENTICATION_FILE} groovy = < ${SCRIPT_BASE_DIR}/groovy/get_node_by_tags.groovy ${@:2} 

