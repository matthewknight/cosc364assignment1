import routing_row


class RoutingTable(object):

    def __init__(self, data):
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]
        print(self.output_ports)
        self.table = []
        self.populateTable()

    def populateTable(self):
        self_entry = routing_row.RoutingRow(0, 0, 0, self.routing_id, 0)
        self.table.append(self_entry)
        output_list = self.output_ports.split(', ')

        for i in output_list:
            values = i.split('-')
            linkCost = values[1]
            destId = values[2]
            nextHopPort = values[0]
            learnedFrom = 0  # ConfigFile

            row = routing_row.RoutingRow(nextHopPort, linkCost, destId, nextHopId, learnedFrom)
            self.table.append(row)
            print()

    def getRoutingTable(self):
        return self.table
