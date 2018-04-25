import sys
import json
import select
import threading
import time
import queue
import random
import pickle
from socket import *
import routing_table
import rip_packet
import routing_row


#TODO when a link goes down, delete entry (garbage collection??)
#TODO work out how to get initial table populated and how to inform other routers


class RipDemon(threading.Thread):

    """Creates an instance of a router that implements the RIP routing Daemon.
    
       Router can be initialised in the command line with:
       
           python rip_demon.py configX.json
           
       Where X is the config file to be used (1-10)
    """

    def __init__(self, filename, intervalBetweenMessages=1, random=False):
        threading.Thread.__init__(self)
        self.filename = filename
        data = json.load(open(self.filename))
        self.config_file_check(data)
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        self.input_sockets_list = []
        self.socket_creator()
        self.routing_table = routing_table.RoutingTable(data)
        self.alive = False
        self.route_timers = []

        # Timer settings
        self.timer_interval = intervalBetweenMessages
        self.timer_value = 0
        self.random = random
        self.ready_for_periodic_update = False


    def socket_creator(self):
        """Initialise the sockets and create a list of socket objects
           based on the number of ports specified in config file"""
        for port in self.input_ports:
            server_socket = socket(AF_INET, SOCK_DGRAM)
            server_socket.bind(('', port))
            self.input_sockets_list.append(server_socket)
            print("Waiting on port " + str(port))


    def run(self):
        while True:

            readable, writable, exceptional = select.select(self.input_sockets_list, [], [], 0.1)
            for s in readable:
                packet, addr = s.recvfrom(2048)

                unpickledRIPReceivedPacket = pickle.loads(packet)
                identical_entry_found = False
                port_to_send = addr[1]
                for found_row in unpickledRIPReceivedPacket.getRIPEntries().getRoutingTable():

                    for current_row in self.routing_table.getRoutingTable():
                        if current_row.row_as_list() == found_row.row_as_list():
                            identical_entry_found = True
                    if unpickledRIPReceivedPacket.getRouterId() != self.routing_id and identical_entry_found == False:
                        #print(found_row)
                        self.process_route_entry(found_row, unpickledRIPReceivedPacket.getRouterId(), port_to_send)
            print(self.routing_table.getRoutingTable())

            self.timer_tick()



    def timer_tick(self):
        # Timer component
        if self.random:
            tickTime = 0.8 + (random.randint(0, 4)) / 10
        else:
            tickTime = 1.0

        time.sleep(tickTime)
        #print("Tick time: ", tickTime)
        # update count value
        self.timer_value += 1
        #print("     Tick count: ", self.timer_value)

        if self.timer_value == self.timer_interval:
            self.ready_for_periodic_update = True
            self.timer_value = 0

        if self.ready_for_periodic_update:
            print("//SENDING MESSAGE//\n")
            self.periodic_update()
            self.ready_for_periodic_update = False

    def process_route_entry(self, row, sending_router_id, port_to_send):
        row_added = False
        #if row.getNextHopPort() in self.routing_table.getInputPorts():
         #   return
        if row in self.routing_table.getRoutingTable():
            return

        destination_router = row.getDestId()
        new_distance = row.getLinkCost()
        for old_row in self.routing_table.getRoutingTable():
            outputs = self.output_ports.split(',')
            for output_entry in outputs:
                output_entry = output_entry.split('-')
                if output_entry[2] == sending_router_id:
                    metric_to_use = output_entry[1]

            if destination_router == old_row.getDestId():
                # process to see if new route is quicker than old, then add
                prelim_dist = int(metric_to_use) + new_distance
                print(prelim_dist, old_row.getLinkCost())
                if prelim_dist < old_row.getLinkCost():
                    row.updateLinkCost(prelim_dist)
                    row.updateNextHopId(sending_router_id)
                    row.updateLearntFrom(sending_router_id)
                    row.updateNextHopPort(port_to_send)
                    if row not in self.routing_table.getRoutingTable():
                        self.routing_table.removeFromRoutingTable(destination_router)
                        self.routing_table.addToRoutingTable(row)
                        row_added = True
                        print("Added entry routing table")
                        print("Removed old entry from the routing table")
        if not row_added:
                #Add new entry to table
            print("Added new entry to row")
            self.routing_table.addToRoutingTable(row)


    def triggered_update(self):
        print("Yeet")
        # if metric == 16, do this
        #TODO

    def periodic_update(self):
        for entry in self.routing_table.getRoutingTable():
            portToSend = entry.getNextHopPort()
            if portToSend != 0:
                packetToSend = rip_packet.RIPPacket(1, self.routing_id, self.routing_table)
                pickledPacketToSend = pickle.dumps(packetToSend)
                self.input_sockets_list[0].sendto(pickledPacketToSend, ("127.0.0.1", portToSend))

    def config_file_check(self, data):
        """The most graceful check to see if the config file has all required attributes."""

        try:
            self.routing_id = data["router-id"]
        except KeyError:
            print("Router id not specified in config file. Exiting...")
            exit(0)
        try:
            self.input_ports = data["input-ports"]
        except KeyError:
            print("Input ports not specified in config file. Exiting...")
            exit(0)
        try:
            self.output_ports = data["outputs"]
        except KeyError:
            print("Output ports not specified in config file. Exiting...")
            exit(0)



    def test_printr(self):
        print("Routing id: " + self.routing_id)
        print(self.input_ports)
        print("Output ports: " + self.output_ports)


if __name__ == "__main__":
    config_file_name = sys.argv[1]
    router = RipDemon(config_file_name, 3, False)
    router.run()




