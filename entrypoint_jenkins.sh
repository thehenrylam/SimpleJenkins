#!/bin/bash

JENKINS_HOME="/var/jenkins_home/"
JENKINS_CLI_JAR="${JENKINS_HOME}/jenkins-cli.jar"
JENKINS_AUTH_FILE="/usr/local/bin/auth_api_ADMIN_shutdown.txt"

download_jenkins_jar() {
        echo "Checking if Jenkins CLI jar file exists."
        if [ ! -e "${JENKINS_CLI_JAR}" ]; then
                echo "Jenkins CLI jar does NOT exist, attempting to grab jenkins-cli."
                # Attempt to download the jenkins CLI jar
                curl http://localhost:8080/jnlpJars/jenkins-cli.jar -o ${JENKINS_CLI_JAR}
        fi
}

# Define the function to handle the graceful shutdown
graceful_shutdown() {
	echo "Received SIGTERM signal. Performing graceful shutdown."
	
	download_jenkins_jar 

	echo "Attempting safe-shutdown of jenkins-cli."
	# Stop Jenkins gracefully using the Jenkins CLI
	java -jar ${JENKINS_CLI_JAR} -s http://localhost:8080 -auth "@${JENKINS_AUTH_FILE}" safe-shutdown

	exit 1
}

# On a new thread: Sleeps for 60 seconds and then attempts to download Jenkins jar
# This 60 second timeout should allow jenkins to fully start up and be able to download the cli jar
sleep 60 && download_jenkins_jar & 
PID_DOWNLOAD=$!

# Register the signal handler function
trap 'graceful_shutdown' SIGTERM

# Boot up Jenkins
exec /usr/bin/tini -- /usr/local/bin/jenkins.sh --prefix="/jenkins"

# Wait for the PID download to finish
wait ${PID_DOWNLOAD}

