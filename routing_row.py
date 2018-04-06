class RoutingRow(object):

    def __init__(self, nextHop, nextHopId, linkCost, destId, learnedFrom):
        self.nextHopPort = nextHop
        self.linkCost = linkCost
        self.destId = destId
        self.nextHopId = nextHopId
        self.learnedFrom = learnedFrom

    def __repr__(self):
        return "{0.nextHopPort} {0.linkCost} {0.destId} {0.nextHopId} {0.learnedFrom}".format(self)

