import gtk
from xml.etree.ElementTree import Element

from panels import GraphicsPanel
from workzones import KSEGraphicWorkzone
from atlas import AtlasCreator
from utils import get_name_from_uri

class Section(gtk.HPaned):
    """
    Contained by : KSEActivityView
    Conceptually, sections represent the parts of the KRF xml.
    As such, they are entitled with the management of these xml parts,
    all operations of addition, deletion and modifications of these nodes
    should if possible be handled here, for the sake of clarity.
    """
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

    def createTree(self, section):
        pass

    def export(self):
        """
        Export current image/sound/animation
        """
        pass

class GraphicSection(Section):
    def __init__(self, instance):
        self.app = instance
        self.graphics = GraphicsPanel(self)
        Section.__init__(self, self.graphics, KSEGraphicWorkzone(self.app))

    def createTree(self, tree):
        self.tree = tree.find("graphics")
        self.workzone.createTree(self.tree)
        resources = self.tree.find("resources")
        if resources != None:
            self.graphics.loadProjectResources(resources)

    def createAtlas(self, options):
        newNode = Element("atlas", attrib = {"name" : options["name"],
                                              "path" : options["location"],
                                             "width" : str(options["width"]),
                                             "height" : str(options["height"])})
        self.tree.append(newNode)
        self.workzone.addAtlas(newNode)

    def addImagesToResources(self, uris):
        node = self.tree.find("resources")
        if node == None:
            node = Element("resources")
            self.tree.append(node)
        for uri in uris:
            newNode = Element("resource", attrib =
                              {"name" : get_name_from_uri(uri),
                               "path" : uri})
            node.append(newNode)

    def export(self):
        self.workzone.export()

    #INTERNAL :

    def addAtlasCb(self, unused):
        AtlasCreator(self)

    # Hackish, connected to the graphics panel's treeview.
    def rowActivatedCb(self, treeview, path, column, model):
        self.app.action_log.begin("add sprite")
        self.workzone.mergeResource(self.graphics.width,
                                    self.graphics.height,
                                    model[path][2])
        self.app.action_log.commit()