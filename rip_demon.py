import sys
import json
import select
import threading
import time
import queue
from socket import *
import routing_table


class RipDemon(threading.Thread):

    """Creates an instance of a router that implements the RIP routing Daemon.
    
       Router can be initialised in the command line with:
       
           python rip_demon.py configX.json
           
       Where X is the config file to be used (1-10)
    """

    def __init__(self, filename):
        threading.Thread.__init__(self)
        self.filename = filename
        data = json.load(open(self.filename))
        self.config_file_check(data)
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        self.input_sockets_list = []
        self.routing_table = routing_table.RoutingTable(data)


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
            readable, writable, exceptional = select.select(self.input_sockets_list, [], [], 0.5)
            for s in readable:
                print("Yeet")
                # Got input from another demon
                    # 1. Unpackage data
                    # 2. Process data
                    # 3. Combine data into own data structure
            if not sendScheduledMessageQueue.empty():
                print("SENDING MESSAGE")
                sendScheduledMessageQueue.queue.clear()


    def config_file_check(self, data):
        """Not the most graceful check to see if the config file has all required attributes."""

        try:
            self.routing_id = data["router-id"]
        except AttributeError:
            print("Router id not specified in config file. Exiting...")
            exit(0)
        try:
            self.input_ports = data["input-ports"]
        except KeyError:
            print("Input ports not specified in config file. Exiting...")
            exit(0)
        try:
            self.output_ports = data["outputs"]
        except AttributeError:
            print("Output ports not specified in config file. Exiting...")
            exit(0)

    def test_printr(self):
        print("Routing id: " + self.routing_id)
        print(self.input_ports)
        print("Output ports: " + self.output_ports)

    def run(self):
        self.input_socket_creator()
        self.listen()


class RIPTimer(threading.Thread):
    '''
    create a thread object that will do the counting in the background
    default interval is 1/1000 of a second
    '''
    def __init__(self, intervalBetweenMessages=1):
        # init the thread
        threading.Thread.__init__(self)
        self.interval = intervalBetweenMessages  # seconds
        # initial value
        self.value = 0
        # controls the while loop in method run
        self.alive = False

    def run(self):
        '''
        this will run in its own thread via self.start()
        '''
        self.alive = True
        while self.alive:
            time.sleep(1)
            # update count value
            self.value += 1
            print(self.value)
            if (self.value == self.interval):
                sendScheduledMessageQueue.put("YES")
                self.value = 0


    def finish(self):
        '''
        close the thread, return final value
        '''
        # stop the while loop in method run
        self.alive = False
        return self.value



if __name__ == "__main__":

    sendScheduledMessageQueue = queue.Queue()

    config_file_name = "config1.json"
    router = RipDemon(config_file_name)
    timer = RIPTimer(5)

    router.start()
    timer.start()

    router.join()
    timer.join()

    #router.test_printr()



