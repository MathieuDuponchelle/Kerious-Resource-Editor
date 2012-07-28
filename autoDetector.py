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

    def coords_compare(self, elem1, elem2):
        if int (elem1[3]) - int(elem2[3]) > 10: # NEXT LINE                                                                                                                                                                                      
            return 1
        elif int (elem1[3]) - int(elem2[3]) < -10: #PREVIOUS LINE                                                                                                                                                                                
            return -1
        return int(elem1[2]) - int(elem2[2]) # SAME LINE

    def getCoordinates(self):
        coordinates = []
        f = open("./lol", 'r')
        for line in f:
            tab = line.split(" ")
            tab[3] = tab[3].rstrip('\n')
            coordinates.append(tab)
        return (sorted(coordinates, cmp = self.coords_compare))

    def setSettings(self, interval, color, matchSize, gravity):
        self.background = color
        self.interval = interval
        self.matchSize = matchSize
        self.gravity = gravity