#!/bin/bash

CURR_SCRIPT_FILEPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_BASE_DIR="$(cd "${CURR_SCRIPT_FILEPATH}/.." && pwd)"
JARDIR="${SCRIPT_BASE_DIR}/jars"

JENKINS_CLI_JAR="${JARDIR}/jenkins-cli.jar"

. ${SCRIPT_BASE_DIR}/config.sh

if [ ! -e "${JENKINS_CLI_JAR}" ]; then
	# Retrieve jenkins-cli.jar
	${SCRIPT_BASE_DIR}/jenkins/download-jenkins-cli.sh
fi

AUTHENTICATION_FILE=$1

if [ ! -e "${AUTHENTICATION_FILE}" ]; then
	echo "Authentication file not found"
	exit 1
fi

java -jar ${JENKINS_CLI_JAR} -s ${JENKINS_URL_LOCAL} -auth "@${AUTHENTICATION_FILE}" "${@:2}"

