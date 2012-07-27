import subprocess

#TODO : use PythonMagick, this will be hard
class autoSpriteDetector:
    """
    Warning, high hack content, radioactive, use with caution.
    Uses a perl script to get the job done.
    """
    def __init__(self):
        self.background = "black"
        self.interval = 10
        self.matchSize = 0
        self.gravity = None

    def startDetection(self, path):
        subprocess.call(["./hack.pl", path, "lol"])

    def getCoordinates(self):
        coordinates = []
        f = open("./lol", 'r')
        for line in f:
            tab = line.split(" ")
            tab[3] = tab[3].rstrip('\n')
            coordinates.append(tab)
        return (coordinates)

    def setSettings(self, interval, color, matchSize, gravity):
        self.background = color
        self.interval = interval
        self.matchSize = matchSize
        self.gravity = gravity