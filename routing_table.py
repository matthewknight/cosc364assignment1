import routing_row, rip_route


class RoutingTable(object):

    def __init__(self, data):
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        self.table = []
        self.routesWithTimers = []
        self.populateTable()
        print(self.table)

    def populateTable(self):
        """Populate the routing table with the information learned from the Configuration files"""
        self_entry = routing_row.RoutingRow(0, 0, 0, self.routing_id, 0)
        #self.addToRoutingTable(self_entry)
        output_list = self.output_ports.split(', ')

        for i in output_list:
            values = i.split('-')
            nextHopPort = values[0]
            linkCost = values[1]
            destId = values[2]
            learnedFrom = 0  # As it was learned from ConfigFile
            row = routing_row.RoutingRow(nextHopPort, destId, linkCost, destId, learnedFrom)
            self.addToRoutingTable(row)

    def getPrettyTable(self):
        for foundRow in self.table:
            if foundRow is not None:
                print("-> {0.destId}, $ = {0.linkCost}, Next hop: {0.nextHopId}".format(foundRow))

    def getRoutingTable(self):
        return self.table

    def getRoutesWithTimers(self):
        return self.routesWithTimers

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
        self.routesWithTimers.append(rip_route.Route(new_row))


    def removeFromRoutingTable(self, destId):
        index = 0
        for row in self.table:

            if row.row_as_list()[2] == int(destId):
                del self.table[index]
            index += 1



