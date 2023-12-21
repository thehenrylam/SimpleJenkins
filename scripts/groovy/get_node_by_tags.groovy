import com.cloudbees.groovy.cps.NonCPS

// Get the nodeNames by label (i.e. tag)
@NonCPS
def nodeNames(label) {
    def nodes = []
    jenkins.model.Jenkins.instance.computers.each { c ->
        if (c.node.labelString.contains(label)) {
            nodes.add(c.node.selfLabel.name)
        }
    }   
    return nodes
}

// Get the intersection of all nodeNames by all tags in the tag_list
def getNodesByTags( tag_list ) {
	output = [] as Set

	for (int i = 0; i < tag_list.size(); i++) {
        	node_names_tag = nodeNames( tag_list[ i ] ) as Set
		if (i == 0) {
			output = node_names_tag
			continue
		}
		if (output.size() == 0) {
			break
		}
		output = output.intersect( node_names_tag )
	}

	return output
}

// Error out if the script is not supplied with at least one tag
if (args.length < 1) {
	throw new Exception("ERROR: Script must be supplied with at least one tag to be used!")
}

// Aggregate all arguments as the combination of nodes to search for
NODE_TAGS = []
for (int i = 0; i < args.length; i++) { NODE_TAGS.add( args[ i ] ) }

node_names = getNodesByTags( NODE_TAGS )
for (int i = 0; i < node_names.size(); i++) {
	println( node_names[i] )
}

