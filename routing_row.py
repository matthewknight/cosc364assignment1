class RoutingRow(object):

    def __init__(self, nextHop, linkCost, destId, nextHopId, learnedFrom):
        self.nextHopPort = nextHop
        self.linkCost = linkCost
        self.destId = destId
        self.nextHopId = nextHopId
        self.learnedFrom = learnedFrom


