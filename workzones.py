import gtk

from status import KSEStatusView

class KSETree(gtk.TreeView):
    def __init__(self):
        self.treestore = gtk.TreeStore(str)
        gtk.TreeView.__init__(self, self.treestore)
        self.show()
        self.set_size_request(400, 250)

class KSEWorkzone(gtk.VPaned):
    def __init__(self):
        gtk.VPaned.__init__(self)
        self.treeview = KSETree()
        self.notebook = KSEStatusView()
        self.add1(self.treeview)
        self.add2(self.notebook)
        self.show()

class KSEGraphicWorkzone(KSEWorkzone):
    def __init__(self):
        KSEWorkzone.__init__(self)
        self.sectionCallbacks = [self._getAtlasFromPath]

    def createTree(self, tree):
        self.tree = tree
        self.model = gtk.TreeStore(str)
        self.treeview.set_model(self.model)
        self._addAtlases()
        self.treeview.connect("row-activated", self._newSelectionCb)

    def addAtlas(self, node):
        self.model.append(self.model.get_iter((0,)), [node.attrib["name"]])
        self.atlases = self.tree.findall("atlas")

    #INTERNAL

    def _addAtlases(self):
        self.atlases = self.tree.findall("atlas")
        atlases = gtk.TreeViewColumn("Graphics")
        cell = gtk.CellRendererText()
        atlases.pack_start(cell, True)
        atlases.add_attribute(cell, "text", 0)
        it = self.model.append(None, ["Atlases"])
        for elem in self.atlases:
            self.model.append(it, [elem.attrib["name"]])
        self.treeview.append_column(atlases)

    def _getAtlasFromPath(self, path):
        return self.atlases[path]

    def _newSelectionCb(self, treeview, path, view_column):
        node = self.sectionCallbacks[path[0]](path[1])
        print path, node
        filePath = None
        try:
            filePath = node.attrib["path"]
            self.notebook.openPath(node, filePath)
        except KeyError:
            ErrorMessage("No Path for this node :/")

    def mergeResource(self, width, height, path):
        self.notebook.mergeResource(width, height, path)