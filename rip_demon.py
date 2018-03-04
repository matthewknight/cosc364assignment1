import sys
import json
from socket import *
class ripDemon(object):
    """Creates an instance of a router that implements the RIP routing Daemon."""
    
    def __init__(self, filename):
        self.filename = filename
        self.routing_id = None
        self.input_ports = None
        self.output_ports = None
        
    
    def load_config(self):
        """Read the config file supplied via the command line."""
        data = json.load(open(self.filename))
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        return self.routing_id, self.input_ports, self.output_ports
    
    
    def socket_creator(self):
        """Initialise the sockets."""
        
        input_ports = list(self.input_ports)
        print(input_ports)
        pass
    
    
    
    def test_printr(self):
        print("Routing id: " + self.routing_id)
        print("Input ports: " + self.input_ports)
        print("Output ports: " + self.output_ports)
        



if __name__ == "__main__":
    config_file_name = sys.argv[1]    
    router = ripDemon(config_file_name)
    router.load_config()
    router.test_printr()
    router.socket_creator()
    
        
