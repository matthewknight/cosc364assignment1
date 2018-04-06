class RoutingRow(object):

    def __init__(self, nextHop, nextHopId, linkCost, destId, learnedFrom):
        self.nextHopPort = nextHop
        self.linkCost = linkCost
        self.destId = destId
        self.nextHopId = nextHopId
        self.learnedFrom = learnedFrom


