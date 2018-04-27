import routing_row, rip_route


class RoutingTable(object):

    def __init__(self, data):
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        self.table = []
        self.neighbourTimers = []
        self.populateTable()
        self.neighbours = []
        self.populateNeighbours()

    def addOneFromConfig(self):
        output_list = self.output_ports.split(', ')
        for i in output_list:
            values = i.split('-')
            nextHopPort = values[0]
            linkCost = values[1]
            destId = values[2]
            learnedFrom = 0  # As it was learned from ConfigFile
            row = routing_row.RoutingRow(nextHopPort, destId, linkCost, destId, learnedFrom)
            if row not in self.table:
                self.addToRoutingTable(row)

    def populateTable(self):
        """Populate the routing table with the information learned from the Configuration files"""

        output_list = self.output_ports.split(', ')

        for i in output_list:
            values = i.split('-')
            nextHopPort = values[0]
            linkCost = values[1]
            destId = values[2]
            learnedFrom = 0  # As it was learned from ConfigFile
            row = routing_row.RoutingRow(nextHopPort, destId, linkCost, destId, learnedFrom)
            self.addToRoutingTable(row)

    def populateNeighbours(self):
        output_list = self.output_ports.split(', ')
        for i in output_list:
            values = i.split('-')
            destId = values[2]
            self.neighbours.append(destId)
            self.neighbourTimers.append(rip_route.Route(destId))

    def getNeighbours(self):
        return self.neighbours

    def getPrettyTable(self):
        for foundRow in self.table:
            if foundRow is not None:
                print("-> {0.destId}, $ = {0.linkCost}, Next hop ID: {0.nextHopId}, Learned from: {0.learnedFrom}".format(foundRow))

    def getRoutingTable(self):
        return self.table

    def getRoutesWithTimers(self):
        return self.neighbourTimers

    def getRouterId(self):
        return self.routing_id

    def getInputPorts(self):
        return self.input_ports

    def getOutputPorts(self):
        return self.output_ports

    def addToRoutingTable(self, new_row):
        if not isinstance(new_row, routing_row.RoutingRow):
            raise TypeError("Non routing-row provided as arg")

        self.table.append(new_row)

    def removeToSwap(self, destId):
        index = 0
        for row in self.table:
            if row.row_as_list()[2] == int(destId):
                del self.table[index]
            index += 1

    def removeFromRoutingTable(self, destId):
        for Row in self.table:
            if int(Row.getDestId()) == int(destId) or int(Row.getNextHopId()) == int(destId) or \
                    (Row.getLearntFromRouter()) == int(destId):
                self.table.remove(Row)



