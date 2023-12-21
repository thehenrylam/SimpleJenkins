#!/bin/bash

CURR_SCRIPT_FILEPATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_BASE_DIR="$(cd "${CURR_SCRIPT_FILEPATH}/.." && pwd)"
JARDIR="${SCRIPT_BASE_DIR}/jars"

JENKINS_CLI_JAR="${JARDIR}/jenkins-cli.jar"

. ${SCRIPT_BASE_DIR}/config.sh

curl -o "${JENKINS_CLI_JAR}" "${JENKINS_URL_LOCAL}/jnlpJars/jenkins-cli.jar"

