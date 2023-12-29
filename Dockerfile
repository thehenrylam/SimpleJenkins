FROM jenkins/jenkins:latest-jdk17

USER root

# Install Python 3 and pip and boto3
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-boto3

USER jenkins

COPY entrypoint_jenkins.sh /usr/local/bin/entrypoint_jenkins.sh
COPY auth_api_ADMIN_shutdown.txt /usr/local/bin/auth_api_ADMIN_shutdown.txt

ENTRYPOINT ["/usr/local/bin/entrypoint_jenkins.sh"]

