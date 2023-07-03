FROM jenkins/jenkins:lts-jdk11

COPY entrypoint_jenkins.sh /usr/local/bin/entrypoint_jenkins.sh
COPY auth_api_ADMIN_shutdown.txt /usr/local/bin/auth_api_ADMIN_shutdown.txt

ENTRYPOINT ["/usr/local/bin/entrypoint_jenkins.sh"]

