import gtk
from xml.etree.ElementTree import Element

from panels import GraphicsPanel, SoundPanel
from workzones import KSEGraphicWorkzone, KSESoundWorkzone
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

    def addToResources(self, uris):
        node = self.tree.find("resources")
        if node == None:
            node = Element("resources")
            self.tree.append(node)
        for uri in uris:
            newNode = Element("resource", attrib =
                              {"name" : get_name_from_uri(uri),
                               "path" : uri})
            node.append(newNode)

class GraphicSection(Section):
    def __init__(self, instance):
        self.app = instance
        self.graphics = GraphicsPanel(self)
        Section.__init__(self, self.graphics, KSEGraphicWorkzone(self.app, self.graphics))

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

    def export(self):
        self.workzone.export()

    #INTERNAL :

    def addAtlasCb(self, unused):
        AtlasCreator(self)

    def importAtlasCb(self, unused):
        chooser = gtk.FileChooserDialog(title="Import atlas", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            newNode = Element("atlas", attrib = {"name" : chooser.get_filename(),
                                                 "path" : chooser.get_filename(),
                                                 "width" : "",
                                                 "height" : ""})
            self.tree.append(newNode)
            self.workzone.addAtlas(newNode)
        chooser.destroy()

    # Hackish, connected to the graphics panel's treeview.
    def rowActivatedCb(self, treeview, path, column, model):
        self.app.action_log.begin("add sprite")
        self.workzone.mergeResource(self.graphics.width,
                                    self.graphics.height,
                                    model[path][2])
        self.app.action_log.commit()

class SoundSection(Section):
    def __init__(self, instance):
        self.app = instance
        self.sounds = SoundPanel(self)
        Section.__init__(self, self.sounds, KSESoundWorkzone(self.app))

    def createTree(self, tree):
        self.tree = tree.find("sounds")
        self.workzone.createTree(self.tree)
        resources = self.tree.find("resources")
        if resources != None:
            self.sounds.loadProjectResources(resources)

    def rowActivatedCb(self, treeview, path, column, model):
        self.app.action_log.begin("add sprite")
        self.workzone.mergeResource(model[path][2], model[path][0])