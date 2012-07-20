from xml.etree.ElementTree import ElementTree

class KrfParser(ElementTree):
    def __init__ (self, name):
        ElementTree.__init__(self)
        self.parse(name)
        #p = self.find("graphics/atlas")
        #print p
        #print dir(p)
        #print p.attrib['name']
        #print p._children

if __name__ == "__main__":
    parser = KrfParser("sample.krf")
