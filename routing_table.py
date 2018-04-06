class RoutingTable(object):

    def __init__(self, data):
        self.routing_id = ''
        self.routing_id = data["router-id"]
        self.input_ports = data["input-ports"]
        self.output_ports = data["outputs"]

    def createRoutingTable(self):

