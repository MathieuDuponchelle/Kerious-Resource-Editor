#!/usr/bin/env python

"""
.. module:: useful_1
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor:: Andrew Carter <andrew@invalid.com>


"""

import gtk

from status import KSEGraphicView, KSESoundView
from error import ErrorMessage
from utils import is_contained_by

class KSETree(gtk.TreeView):
    def __init__(self):
        self.treestore = gtk.TreeStore(str)
        gtk.TreeView.__init__(self, self.treestore)
        self.show()
        self.set_size_request(400, 250)

class KSEWorkzone(gtk.VPaned):
    """
    Contained by : Sections
    Workzones contain two things : An xml prettifier displaying the content of
    their managed section, and a "Status view", for lack of a better word,
    where the user can interact with the content, for example the atlases.
    @cvar current : Path of the current atlas in the model
    """
    def __init__(self):
        gtk.VPaned.__init__(self)
        scrolledWindow = gtk.ScrolledWindow()
        self.treeview = KSETree()
        scrolledWindow.add(self.treeview)
        scrolledWindow.set_size_request(-1, 200)
        #scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add1(scrolledWindow)
        self.add2(self.notebook)
        self.show_all()

    def _loadAtlasFromXml(self, node, path):
        self.current = path
        filePath = None
        try:
            filePath = node.attrib["path"]
            self.notebook.loadAtlasFromXml(node, filePath)
        except KeyError:
            ErrorMessage("No Path for this node :/")

    def createTree(self, tree):
        self.tree = tree
        self.model = gtk.TreeStore(str)
        self.treeview.set_model(self.model)
        self.treeview.connect("row-activated", self._newSelectionCb)

    def _newSelectionCb(self, treeview, path, view_column):
        if len(path) < 2:
            return
        node = self.sectionCallbacks[path[0]](path[1])
        self._loadAtlasFromXml(node, path)

    def export(self):
        pass

class KSEGraphicWorkzone(KSEWorkzone):
    def __init__(self, instance):
        self.app = instance
        self.notebook = KSEGraphicView(self)
        KSEWorkzone.__init__(self)
        self.sectionCallbacks = [self._getAtlasFromPath]
        self.current = None


    def addAtlas(self, node):
        self.model.append(self.model.get_iter((0,)), [node.attrib["name"]])
        self.atlases = self.tree.findall("atlas")

    def addSpriteForAtlas(self, atlasNode, node):
        atlas = self.model.get_iter(self.current)
        self.model.append(atlas, [node.attrib["name"]])

    def export(self):
        self.notebook.export()

    def mergeResource(self, width, height, path):
        self.notebook.mergeResource(width, height, path)

    def createTree(self, tree):
        KSEWorkzone.createTree(self, tree)
        self._addAtlases()

    #INTERNAL

    def _addAtlases(self):
        self.atlases = self.tree.findall("atlas")
        atlases = gtk.TreeViewColumn("Graphics")
        cell = gtk.CellRendererText()
        atlases.pack_start(cell, True)
        atlases.add_attribute(cell, "text", 0)
        it = self.model.append(None, ["Atlases"])
        for elem in self.atlases:
            at = self.model.append(it, [elem.attrib["name"]])
            sprites = elem.findall("sprite")
        self.treeview.append_column(atlases)

    def _getAtlasFromPath(self, path):
        return self.atlases[path]

    def _spriteAddedCb(self, atlas, sprite):
        atlas = self.model.get_iter(self.current)
        sprite.iter = self.model.append(atlas, [sprite.path])

    def _spriteRemovedCb(self, atlas, sprite):
        atlas = self.model.get_iter(self.current)
        self.model.remove(sprite.iter)

class KSESoundWorkzone(KSEWorkzone):
    def __init__(self, instance):
        self.app = instance
        self.notebook = KSESoundView(self)
        KSEWorkzone.__init__(self)

    def mergeResource(self, uri, name):
        self.notebook.addSound(uri, name)

    def createTree(self, tree):
        KSEWorkzone.createTree(self, tree)
        self.notebook.loadSounds(tree)