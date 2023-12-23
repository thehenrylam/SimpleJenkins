import hudson.model.Computer.ListPossibleNames

def GetPrivateIpAddress( node_name ) {
	def node = jenkins.model.Jenkins.instance.getNode( node_name )
	if (node.computer.isOnline() == false) {
		System.err.println("WARN: The node '${node_name}' is disconnected, Skipping IP Address Acquisition!")
		return null
	}
	def node_channel = node.computer.getChannel()
	def ip_addresses = node_channel.call(new ListPossibleNames())
	// Get the last ip_address in the list 
	// (Which usually indicates the final destination of the target node)
	return ip_addresses.last()
}

def GetPortNumber( node_name ) {
	def node = jenkins.model.Jenkins.instance.getNode( node_name )
	if (node.computer.isOnline() == false) {
		System.err.println("WARN: The node '${node_name}' is disconnected, Skipping Port Number Acquisition!")
		return null
	}
	// In the current state of the implementation, we asume that it is 25565
	return "25565"
}

// def node = jenkins.model.Jenkins.instance.getNode( node_name )
// println node.computer.getChannel().call(new ListPossibleNames())

// Error out if the script is not supplied with at least one tag
if (args.length < 1) {
	throw new Exception("ERROR: Script must be supplied with the node name! (e.g. \"node_name_1,node_name_2,...,node_name_n\" Note: No spaces between commas!)")
}

def comma_separated_node_names = args[0]
def list_of_node_names = comma_separated_node_names.split(',')

def list_of_interface_information = []
for (int i = 0; i < list_of_node_names.size(); i++) {
	ip_address = GetPrivateIpAddress( list_of_node_names[i] )
	port_number = GetPortNumber( list_of_node_names[i] )
	println("${list_of_node_names[i]},${ip_address},${port_number}")
}


