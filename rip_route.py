class Route(object):

    def __init__(self, destId):
        self.destId = destId
        self.timeoutTime = 0
        self.hasTimeout = False
        self.garbageCollectionTime = 0

    def __repr__(self):
        return "-> {0.row.destId} {0.hasTimeout} Time: {0.timeoutTime}\n".format(self)

    def setRouteAsTimedOut(self):
        self.hasTimeout = True

    def hasTimedOut(self):
        return self.hasTimeout

    def incrementTimeoutTime(self):
        self.timeoutTime += 1

    def incrementGarbageCollectionTime(self):
        self.garbageCollectionTime += 1

    def getTimeoutTime(self):
        return self.timeoutTime

    def getGarbageCollectionTime(self):
        return self.garbageCollectionTime

    def resetTime(self):
        self.timeoutTime = 0
        self.garbageCollectionTime = 0

    def getDestId(self):
        return self.destId

