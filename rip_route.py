class Route(object):

    def __init__(self, row):
        ##TODO change row to just destId -> TMI
        self.row = row
        self.timeoutTime = 0
        self.garbageCollectionTime = 0

    def incrementTime(self):
        self.timeoutTime += 1
        self.garbageCollectionTime += 1

    def getTimeoutTime(self):
        return self.timeoutTime

    def getGarbageCollectionTime(self):
        return self.garbageCollectionTime

    def resetTime(self):
        self.timeoutTime = 0
        self.garbageCollectionTime = 0

    def getRow(self):
        return self.row

