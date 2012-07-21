import gtk

from panels import GraphicsPanel
from workzones import KSEGraphicWorkzone

class Section(gtk.HPaned):
    def __init__(self, panel, workzone):
        gtk.HPaned.__init__(self)
        self.workzone = workzone
        self.panel = panel
        self.workzone.set_size_request(1600, -1)
        self.add1(self.workzone)
        self.add2(self.panel)
        self.show()

    def resetTree(self):
        pass
    
    #subclass This
    def createTree(self, section):
        pass

class GraphicSection(Section):
    def __init__(self, window):
        self.graphics = GraphicsPanel(self)
        Section.__init__(self, self.graphics, KSEGraphicWorkzone())
        self.win = window

    def createTree(self, tree):
        self.tree = tree.find("graphics")
        self.workzone.createTree(self.tree)

    def createAtlas(self, options):
        newNode = Element("atlas", attrib = {"name" : options["name"],
                                              "path" : options["location"],
                                             "width" : options["width"],
                                             "height" : options["height"]})
        self.tree.append(newNode)
        self.workzone.addAtlas(newNode)

    def addAtlasCb(self, unused):
        AtlasCreator(self)

    def rowActivatedCb(self, treeview, path, column, model):
        self.workzone.mergeResource(self.graphics.width, self.graphics.height, model[path][1])