import sys
import json
import select
import threading
import time
import copy
import random
import pickle
from socket import *
import routing_table
import rip_packet


class RipDemon(threading.Thread):

    """Creates an instance of a router that implements the RIP routing Daemon.
    
       Router can be initialised in the command line with:
       
           python rip_demon.py configX.json
           
       Where X is the config file to be used (1-10)
    """

    def __init__(self, filename, intervalBetweenMessages=1, random=False, timeoutPeriod=15, garbageCollectionPeriod=15):
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

        print(self.routing_table.getPrettyTable())

        # Timer settings
        self.timer_interval = intervalBetweenMessages
        self.timer_value = 0
        self.triggered_update_cooldown_timer_value = 0
        self.hasRecentlyTriggeredUpdate = False
        self.timeout_period = timeoutPeriod
        self.garbage_collection_period = garbageCollectionPeriod
        self.random = random
        self.ready_for_periodic_update = False
        self.ready_for_triggered_update = False

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

                # Reset timeout timer of destId of received packed
                receivedFromDestId = unpickledRIPReceivedPacket.getRouterId()
                for Route in self.routing_table.getRoutesWithTimers():
                    if Route.getDestId() == receivedFromDestId:
                        Route.resetTime()

                identical_entry_found = False
                port_to_send = addr[1]
                for found_row in unpickledRIPReceivedPacket.getRIPEntries().getRoutingTable():
                    for current_row in self.routing_table.getRoutingTable():
                        if current_row.row_as_list() == found_row.row_as_list():
                            identical_entry_found = True

                    if unpickledRIPReceivedPacket.getRouterId() != self.routing_id and identical_entry_found == False:
                        self.process_route_entry(found_row, unpickledRIPReceivedPacket.getRouterId(), port_to_send)

            self.timer_tick()

    def timer_tick(self):
        # Timer component
        if self.random:
            tickTime = 0.8 + (random.randint(0, 4)) / 10
        else:
            tickTime = 1.0

        time.sleep(tickTime)
        # update count value
        self.timer_value += 1

        if self.timer_value == self.timer_interval:
            self.ready_for_periodic_update = True
            self.timer_value = 0

        if self.ready_for_periodic_update:
            self.periodic_update()
            self.ready_for_periodic_update = False

        self.check_for_changed_routes()

        # Check if has recently sent a triggered update
        if self.ready_for_triggered_update:
            if not self.hasRecentlyTriggeredUpdate:
                self.triggered_update()
                self.triggered_update_cooldown_timer_value = 0
                self.ready_for_triggered_update = False
                self.hasRecentlyTriggeredUpdate = True
            else:
                self.triggered_update_cooldown_timer_value += 1
                if self.triggered_update_cooldown_timer_value >= (random.randint(1, 5)):
                    self.hasRecentlyTriggeredUpdate = False

        for Route in self.routing_table.getRoutesWithTimers():
            if Route.hasTimedOut():
                Route.incrementGarbageCollectionTime()
                if Route.getGarbageCollectionTime() == self.garbage_collection_period:
                    self.routing_table.removeFromRoutingTable(Route.getDestId())
                    self.routing_table.removeFromRoutingTable(Route.getDestId())
            else:
                Route.incrementTimeoutTime()
                if Route.getTimeoutTime() == self.timeout_period:
                    self.set_row_as_timed_out(Route)

    def check_for_changed_routes(self):
        for Row in self.routing_table.getRoutingTable():
            if Row.hasChanged():
                self.ready_for_triggered_update = True
                return

        neighbour_rows = []
        non_neighbour_rows = copy.deepcopy(self.routing_table.getRoutingTable())

        for Route in self.routing_table.getRoutesWithTimers():
            for Row in self.routing_table.getRoutingTable():
                if int(Route.getDestId()) == int(Row.getDestId()):
                    neighbour_rows.append(Row)
                if int(Route.getDestId()) == int(Row.getDestId()) and not Route.hasTimedOut() and Row.getLinkCost() == 16:
                    self.routing_table.removeFromRoutingTable(Route.getDestId())
                    return

        for Row in neighbour_rows:
            non_neighbour_rows.remove(Row)

        for Row in non_neighbour_rows:
            if Row.getLinkCost() == 16:
                self.routing_table.removeFromRoutingTable(Row.getDestId())

    def set_row_as_timed_out(self, route):
        route.setRouteAsTimedOut()
        for Row in self.routing_table.getRoutingTable():
            print(Row.getDestId(), " ", route.getDestId())
            if int(Row.getDestId()) == int(route.getDestId()):
                Row.updateLinkCost(16)
                Row.setHasBeenChanged()

    def reset_timers_of_dest(self, destId):
        for Route in self.routing_table.getRoutesWithTimers():
            if int(Route.getDestId()) == int(destId):
                Route.resetTime()

    def process_route_entry(self, new_row, sending_router_id, port_to_send):
        # If there's no entry for the senders id
        flag = False
        for row in self.routing_table.getRoutingTable():
            if int(row.getDestId()) == int(sending_router_id):
                flag = True
                break
        if not flag:
            self.routing_table.addOneFromConfig()

        # If next hop port is one of your own, skip this entry
        if new_row.getNextHopPort() in self.routing_table.getInputPorts():
            return
        # If row already exists exactly, skip this entry also
        if new_row in self.routing_table.getRoutingTable():
            return

        destination_router = new_row.getDestId()
        new_distance = new_row.getLinkCost()

        # If router receives a update to a link with metric 16 (i.e that link is down)
        if new_distance == 16:
            for row in self.routing_table.getRoutingTable():
                if row.getDestId() == destination_router:
                    row.updateLinkCost(16)
                    row.setHasBeenChanged()
                    break

        for old_row in self.routing_table.getRoutingTable():
            # Make the route non modifiable when it hits 16
            if old_row.getLinkCost() == 16:
                return

            cost_to_router_row_received_from = 16
            costFoundFlag = False
            for current_row in self.routing_table.getRoutingTable():
                if int(current_row.getDestId()) == int(sending_router_id):
                    cost_to_router_row_received_from = current_row.getLinkCost()
                    costFoundFlag = True

            if destination_router == old_row.getDestId() and costFoundFlag:
                # Process to see if new route is quicker than old, then add
                prelim_dist = int(cost_to_router_row_received_from) + new_distance

                if prelim_dist < old_row.getLinkCost():
                    new_row.updateLinkCost(prelim_dist)
                    new_row.updateNextHopId(sending_router_id)
                    new_row.updateLearntFrom(sending_router_id)
                    new_row.updateNextHopPort(port_to_send)
                    new_row.setHasBeenChanged()

                    self.reset_timers_of_dest(new_row.getDestId())

                    if new_row not in self.routing_table.getRoutingTable():
                        self.routing_table.removeToSwap(destination_router)
                        self.routing_table.addToRoutingTable(new_row)
                        print("Added new route -> {0}, $ = {1}".format(new_row.getDestId(), new_row.getLinkCost()))
                        print("Removed old entry from the routing table")
                        print(self.routing_table.getPrettyTable())

            entryExists = False
            for current_row in self.routing_table.getRoutingTable():
                if current_row.getDestId() == new_row.getDestId():
                    entryExists = True

            if not entryExists:
                if not cost_to_router_row_received_from + new_row.getLinkCost() > 15:
                    new_row.updateLinkCost(cost_to_router_row_received_from + new_row.getLinkCost())
                    new_row.setHasBeenChanged()
                    new_row.updateLearntFrom(sending_router_id)
                    new_row.updateNextHopId(sending_router_id)
                    new_row.updateNextHopPort(port_to_send)
                    self.routing_table.addToRoutingTable(new_row)
                    print("Adding new neighbour ", new_row.getDestId())
                    print(self.routing_table.getPrettyTable())

    def triggered_update(self):
        print("Calling triggered update...", self.triggered_update_cooldown_timer_value)
        print(self.routing_table.getPrettyTable())

        output_list = self.output_ports.split(", ")
        for entry in output_list:
            entry = entry.split('-')
            outbound_router_id = entry[2]
            entry = entry[0]
            portToSend = int(entry)

            # Don't send to self
            if portToSend != 0:
                tableToSend = copy.deepcopy(self.routing_table)
                # Remove entries that haven't changed
                for Row in tableToSend.getRoutingTable():
                    if not Row.hasChanged():
                        tableToSend.removeToSwap(Row.getDestId())
                    if int(outbound_router_id) == int(Row.getLearntFromRouter()):
                        Row.updateLinkCost(16)

                packetToSend = rip_packet.RIPPacket(1, self.routing_id, tableToSend)
                pickledPacketToSend = pickle.dumps(packetToSend)
                self.input_sockets_list[0].sendto(pickledPacketToSend, ("127.0.0.1", portToSend))

        # Set the changed flag to false in our current routing table
        for ourRow in self.routing_table.getRoutingTable():
            ourRow.resetChanged()

    def periodic_update(self):

        output_list = self.output_ports.split(", ")
        for entry in output_list:
            entry = entry.split('-')
            outbound_router_id = entry[2]
            entry = entry[0]
            portToSend = int(entry)
            print("Calling periodic update to ", outbound_router_id)

            # Dont send to self
            if portToSend != 0:
                tableToSend = copy.deepcopy(self.routing_table)

                for row in tableToSend.getRoutingTable():
                    if int(outbound_router_id) == int(row.getLearntFromRouter()):
                        row.updateLinkCost(16)

                packetToSend = rip_packet.RIPPacket(1, self.routing_id, tableToSend)
                pickledPacketToSend = pickle.dumps(packetToSend)
                self.input_sockets_list[0].sendto(pickledPacketToSend, ("127.0.0.1", portToSend))

        print("My Routing Table")
        print(self.routing_table.getPrettyTable())

    def config_file_check(self, data):
        """The most graceful check to see if the config file has all required attributes."""
        try:
            self.routing_id = data["router-id"]
            if int(self.routing_id) < 1 or int(self.routing_id) > 64000:
                raise ValueError("Invalid router ID(s). Exiting...")
        except KeyError:
            print("Router id not specified in config file. Exiting...")
            exit(0)
        try:
            self.input_ports = data["input-ports"]
            for port in self.input_ports:
                if port < 1024 or port > 64000:
                    raise ValueError("Input port number(s) out of range. Exiting...")
        except KeyError:
            print("Input ports not specified in config file. Exiting...")
            exit(0)
        try:
            self.output_ports = data["outputs"]
            output_test_list = self.output_ports.split(', ')
            for entry in output_test_list:
                port = entry.split('-')
                port = int(port[0])
                if port < 1024 or port > 64000:
                    raise ValueError("Output port(s) out of range. Exiting...")
        except KeyError:
            print("Output ports not specified in config file. Exiting...")
            exit(0)


if __name__ == "__main__":
    config_file_name = sys.argv[1]
    router = RipDemon(config_file_name, 3, True, 7, 15)
    router.run()




