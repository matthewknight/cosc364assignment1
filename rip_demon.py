import sys
import json
from socket import *
class ripDemon(object):
    """Creates an instance of a router that implements the RIP routing Daemon.
    
       Router can be initialised in the command line with:
       
           python rip_demon.py configX.json
           
       Where X is the config file to be used (1-10)
    """
    
    def __init__(self, filename):
        self.filename = filename
    
    def load_config(self):
        """Read the config file supplied via the command line."""
        data = json.load(open(self.filename))
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        return self.routing_id, self.input_ports, self.output_ports
    
    
    def input_socket_creator(self):
        """Initialise the sockets and create a list of socket objects
           based on the number of ports specified in config file"""
        num_ports = len(self.input_ports)
        self.sockets_list = []
        
        for port in self.input_ports:
            
            serverSocket = socket(AF_INET, SOCK_DGRAM)
            serverSocket.bind(('', port))
            self.sockets_list.append(serverSocket)
            print("waiting on port " + str(port))
        
        
    
    
    
    def test_printr(self):
        print("Routing id: " + self.routing_id)
        print(self.input_ports)
        print("Output ports: " + self.output_ports)
        



if __name__ == "__main__":
    config_file_name = sys.argv[1]    
    router = ripDemon(config_file_name)
    router.load_config()
    #router.test_printr()
    router.input_socket_creator()
    
        
