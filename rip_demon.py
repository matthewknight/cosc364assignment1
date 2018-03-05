import sys
import json
import select
from socket import *


class RipDemon(object):
    """Creates an instance of a router that implements the RIP routing Daemon.
    
       Router can be initialised in the command line with:
       
           python rip_demon.py configX.json
           
       Where X is the config file to be used (1-10)
    """
    
    def __init__(self, filename):
        self.filename = filename
        data = json.load(open(self.filename))

        self.input_ports = data["input-ports"]
        self.routing_id = data["router-id"]
        self.output_ports = data["outputs"]
        self.input_sockets_list = []

    def input_socket_creator(self):
        """Initialise the sockets and create a list of socket objects
           based on the number of ports specified in config file"""
        for port in self.input_ports:
            server_socket = socket(AF_INET, SOCK_DGRAM)
            server_socket.bind(('', port))
            self.input_sockets_list.append(server_socket)
            print("Waiting on port " + str(port))

    def listen(self):
        while True:
            readable, writable, exceptional = select.select(self.input_sockets_list, [], [])
            for s in readable:
                print("Yeet")
                # Got input from another demon
                    # 1. Unpackage data
                    # 2. Process data
                    # 3. Combine data into own data structure

    def test_printr(self):
        print("Routing id: " + self.routing_id)
        print(self.input_ports)
        print("Output ports: " + self.output_ports)


if __name__ == "__main__":
    config_file_name = sys.argv[1]    
    router = RipDemon(config_file_name)
    #router.test_printr()
    router.input_socket_creator()
    router.listen()


