class RoutingRow(object):

    def __init__(self, nextHop, nextHopId, linkCost, destId, learnedFrom):
        self.nextHopPort = int(nextHop)
        self.linkCost = int(linkCost)
        self.destId = int(destId)
        self.nextHopId = int(nextHopId)
        self.learnedFrom = int(learnedFrom)

    def __repr__(self):
        return "{0.nextHopPort} {0.linkCost} {0.destId} {0.nextHopId} {0.learnedFrom}".format(self)


    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def getNextHopPort(self):
        return self.nextHopPort

    def getLinkCost(self):
        return self.linkCost

    def getDestId(self):
        return self.destId

    def getNextHopId(self):
        return self.nextHopId

    def getLearntFromRouter(self):
        return self.learnedFrom

    def updateLinkCost(self, cost):
        self.linkCost = cost

    def updateNextHopId(self, hop):
        self.nextHopId = hop

    def updateNextHopPort(self, port):
        self.nextHopPort = port

    def updateLearntFrom(self, id):
        self.learnedFrom = id
    def row_as_list(self):
        return [self.nextHopPort, self.linkCost, self.destId, self.nextHopId, self.learnedFrom]

