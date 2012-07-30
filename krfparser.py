from xml.etree.ElementTree import ElementTree

class KrfParser(ElementTree):
    def __init__ (self, name):
        ElementTree.__init__(self)
        self.parse(name)

    def isValid(self):
        if self.find("graphics") == None:
            return (False)
        if self.find("sounds") == None:
            return (False)
        if self.find("music") == None:
            return (False)
        return (True)

if __name__ == "__main__":
    parser = KrfParser("sample.krf")
