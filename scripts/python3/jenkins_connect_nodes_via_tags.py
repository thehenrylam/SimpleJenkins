#!/bin/python3

import sys 
import os
import subprocess 


def executeGetNodesByTags( auth_file, node_tags ):
    output = []

    base_script_directory = getScriptFilepath()
    script_get_nodes_by_tags = f"{base_script_directory}/jenkins/jenkins-get-node-by-tags.sh"
    try:
        cmd_get_nodes_by_tags = f"{script_get_nodes_by_tags} {auth_file} {' '.join(node_tags)}"
        prc = subprocess.run(['bash'] + cmd_get_nodes_by_tags.split(), capture_output=True, text=True, check=True)
        print(f"Executed : {cmd_get_nodes_by_tags}")
        print(prc.stdout.strip())
        output = prc.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error executing the script: {e}")
        print("Error Output:") 
        print(e.stderr) 
    return output 

def executeConnectToNode( auth_file, node_name ):
    base_script_directory = getScriptFilepath()
    script_connect_to_node = f"{base_script_directory}/jenkins/jenkins-connect-to-node.sh"
    try:
        cmd_connect_to_node = [f"{script_connect_to_node}", f"{auth_file}", f"{node_name}"]
        prc = subprocess.run(['bash'] + cmd_connect_to_node, capture_output=True, text=True, check=True)
        print(f"Executed : {' '.join(cmd_connect_to_node)}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing the script: {e}")
        print("Error Output:")
        print(e.stderr)
    return

def main( jenkins_auth_file, node_tags ): 
    jenkins_nodes = executeGetNodesByTags( jenkins_auth_file, node_tags )  

    for n in jenkins_nodes:
        executeConnectToNode( jenkins_auth_file, n )

    return

def getScriptFilepath():
    curr_script_directory = os.path.dirname(os.path.abspath(__file__))
    curr_script_directory_tokens = curr_script_directory.split('/')
    base_script_directory_tokens = curr_script_directory_tokens[:-1]
    base_script_directory = '/'.join(base_script_directory_tokens)
    return base_script_directory

def displayHelp(): 
    print(f"{sys.argv[0]} <jenkins_auth_file> <node tag #1> <node tag #2> ... <node tag #n>") 
    return


if __name__ == "__main__":
    if (len(sys.argv) < 3): 
        displayHelp()
        exit(1)

    jenkins_auth_file = sys.argv[1]
    node_tags = sys.argv[2:]

    main( jenkins_auth_file, node_tags )  


