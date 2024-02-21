#!/bin/python3

import sys
import os
import subprocess
import json

def parseParameters( parameters ):
    output = []
    if ( len(parameters) == 0):
        return output
    for p in parameters:
        k = p["key"]
        v = p["value"]
        output += [ f"-p" ] + [ f"{k}={v}" ]
    return output

def main( jenkins_auth_file, jenkins_job_file ):
    d = None
    with open(jenkins_job_file) as json_data:
        d = json.load(json_data)
    if d is None:
        raise Exception(f"Json data from '{jenkins_job_file}' could not be loaded!")

    # print(d)

    base_script_directory = getScriptFilepath()
    jenkins_cli_script = f"{base_script_directory}/jenkins/jenkins-cli.sh"

    job_name = d["job"]
    job_parameters = parseParameters( d["parameters"] )

    cmd = [ jenkins_cli_script, jenkins_auth_file, "build", job_name ] + job_parameters + [ "-f", "-v" ]

    # cmd = f"{jenkins_cli_script} {jenkins_auth_file} build {job_name} {job_parameters} -f -v"
    # print(cmd)
    exeCmd(cmd)

    return

def exeCmd( cmd ):
    output = []
    try:
        prc = subprocess.run([ "bash" ] + cmd, capture_output=True, text=True, check=True)
        print(f"Executed : {' '.join(cmd)}")
        print(prc.stdout.strip())
        output = prc.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error executing the script: {e}")
        print("Error Output:")
        print(e.stderr)
    return output

def getScriptFilepath():
    curr_script_directory = os.path.dirname(os.path.abspath(__file__))
    curr_script_directory_tokens = curr_script_directory.split('/')
    base_script_directory_tokens = curr_script_directory_tokens[:-1]
    base_script_directory = '/'.join(base_script_directory_tokens)
    return base_script_directory

def displayHelp():
    print(f"{sys.argv[0]} <jenkins_auth_file> <jenkins_job_information.json>")
    return

if __name__ == "__main__":
    if (len(sys.argv) < 2): 
        displayHelp()
        exit(1)

    jenkins_auth_file = sys.argv[1]
    jenkins_job_file = sys.argv[2]

    main( jenkins_auth_file, jenkins_job_file )

