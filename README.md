# SimpleJenkins 
_Jenkins Made Simple_

## Simple Setup 🏗️

### Step 1: Configure Credentials
Create `./ansible/group_vars/jenkins_credentials.yml` and with the credentials to what you desire.
Use `./ansible/group_vars/jenkins_credentials.TEMPLATE.yml` as a starting point.
_TIP: Since this file stores sensitive information, consider storing this file in a secured location and keeping it here only when SimpleJenkins is being configured with passwords_

### Step 2: Execute Setup Playbook
Execute the following command:
``` SHELL
ansible-playbook ansible/playbooks/deploy-config_standard.yml
```

## Simple Usage 🚀

### Start Application
``` SHELL
# `sudo` must be used for the default usage of docker 
# _NOTE_: --build is meant to make sure that the image is built (since we're using a custom image that supports plugins.txt)
sudo docker compose up --build -d
```

### Stop Application
``` SHELL
# `sudo` must be used for the default usage of docker 
sudo docker compose down
```

### Access Jenkins
1. Open your browser, navigate to the URL `http://<jenkins-host-ip>:8080/jenkins/`
2. Use the `admin` password that you had set up with `./ansible/group_vars/jenkins_credentials.yml` 
3. _TIP: Using Jenkins without a reverse proxy is not recommended since network traffic is not secured. If you want a quick and easy reverse proxy setup, consider using [SimpleNginx](https://github.com/thehenrylam/SimpleNginx)_ 

## Simple Configuration 🛠️

...

## Simple Resources 📚

Documentation on Jenkins Docker:
https://github.com/jenkinsci/docker/blob/master/README.md

Documentation on Jenkins Pipeline:
https://www.jenkins.io/doc/book/pipeline/



