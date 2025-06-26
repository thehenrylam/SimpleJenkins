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

### How to extract Jenkins Configuration as Code (CasC) for repo/ansible_casc/jenkins.yaml

1. Login as an admin user
2. Navigate to `${JENKINS_URL}/manage/configuration-as-code/` (e.g. https://127.0.0.1/jenkins/manage/configuration-as-code/)
3. Click on the `View Configuration` button to view and/or extract the CasC with your current changes. 
4. (Optional): You may click on the `Download Configuration` button to download it where `jenkins.yaml` is at. (Not recommended if you're new to using this repo, since it will overwrite your current configuration)
5. Remove and/or template certain variables in the new CasC YAML config. (e.g. `unclassified.location.url` to help allow Jenkins to avoid a hardcoded Jenkins URL)

### How to extract Jenkins List of Plugins for repo/plugins.txt

1. Login as an admin user
2. Navigate to `$(JENKINS_URL)/manage/script/` (e.g. https://127.0.0.1/jenkins/manage/script/)
3. Execute the following: 
``` groovy
// Get the array of plugins from jenkins plugin manager, sort it, and then print out each plugin with its corresponding name and verion
def array_of_plugins = new ArrayList(Jenkins.instance.pluginManager.plugins)
    .sort { it.shortName }
    .each { println("${it.shortName}:${it.version}") }
// This print function removes the "Result: [...]" at the very end, which is undesirable when wanting an output that ou can readily copy-paste to plugins.txt
println("")
``` 
4. Copy the output of the `Script Console` 
5. Place the output into repo/plugins.txt

## Simple Resources 📚

Documentation on Jenkins Docker:
https://github.com/jenkinsci/docker/blob/master/README.md

Documentation on Jenkins Pipeline:
https://www.jenkins.io/doc/book/pipeline/



