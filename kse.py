#!/usr/bin/env python

import sys
import gtk
import gobject
import argparse
import logging
import sys

from krfparser import KrfParser
from photoshop import Photoshop
from optparse import OptionParser
from error import ErrorMessage

WINDOWTITLE="Kerious Ressources Editor"
WINWIDTH=1024
WINHEIGHT=768
BORDERWIDTH=2

IMAGE_ADD="assets/list-add.svg"
IMAGE_NEW="assets/document-new.png"
IMAGE_OPEN="assets/document-open.png"
IMAGE_SAVE="assets/document-save.png"
IMAGE_SAVE_AS="assets/document-save-as.png"

###
# CLASSES
###

class BaseMenu(gtk.MenuItem):
    def __init__(self, menuName):
        gtk.MenuItem.__init__(self, menuName)
        self.menu = gtk.Menu()
        self.set_submenu(self.menu)
        self.show()
        
    def addEntry(self, entryName, callBack = None, show = True):
        item = gtk.MenuItem(entryName)
        if callBack is not None:
            item.connect("activate", callBack)
        self.menu.append(item)
        if show:
            item.show()
            
class Button(gtk.Button):
    FILL = 0
    PACKSTART = 1
    PACKEND = 2
    
    def __init__(self, name = None, pack = None, packType = None, show = True, callBack = None, imageLink = None):        
        gtk.Button.__init__(self)
        self.constructButton(name, imageLink)
        if packType is None:
            packType = Button.FILL
        if pack is not None:
            if packType == Button.FILL:
                pack.add(self)
            elif packType == Button.PACKSTART:
                pack.pack_start(self, False, False, 0)
            elif packType == Button.PACKEND:
                pack.pack_end(self, False, False)
            else:
                print "Button Error : Invalid packType", packType
        if callBack is not None:
            self.connect("clicked", callBack)
        if show:
            self.show()
            
    def constructButton(self, name, imageLink):
        nameLabel = None
        image = None
        if name is not None:
            nameLabel = gtk.Label(name)
            nameLabel.show()
        if imageLink is not None:
            image = gtk.Image()
            image.set_from_file(imageLink)
            image.show()
        if nameLabel is not None and image is not None:
            box = gtk.HBox()
            box.show()
            box.pack_start(image, False, False)
            box.add(nameLabel)
            self.add(box)
        elif nameLabel is not None:
            self.add(nameLabel)
        elif image is not None:
            self.add(image)
        
        
class FileMenu(BaseMenu):
    def __init__(self, buttonBox, activityView):
        BaseMenu.__init__(self, "File")
        self.addEntry("New", None)
        self.addEntry("Open", self.openFileAction)
        self.addEntry("Save", None)
        self.addEntry("Save As...", None)
        self.addEntry("Quit", None)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_NEW)
        Button(pack=buttonBox, packType=Button.PACKSTART, callBack=self.openFileAction, imageLink=IMAGE_OPEN)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE_AS)
        
        self.activityView = activityView
        
    def openFileAction(self, fileMenu):
        chooser = gtk.FileChooserDialog(title="Choose your file", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.add_pattern("*.krf")
        filter.set_name("Kerious Ressources File (*.ksf)")
        chooser.add_filter(filter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.activityView.openFile(chooser.get_filename())
        chooser.destroy()
    
class SectionMenu(BaseMenu):
    def __init__(self):
        BaseMenu.__init__(self, "Sections")
        self.addEntry("Graphics", None)
        self.addEntry("Sound Effects", None)
        self.addEntry("Musics", None)
        
class AboutMenu(BaseMenu):
    def __init__(self):
        BaseMenu.__init__(self, "Infos")
        self.addEntry("About Kerious", None)
        self.addEntry("About Kerious Ressources Editor", None)

class KSEMenuBar(gtk.MenuBar):
    def __init__(self, toolbox, activityView):
        gtk.MenuBar.__init__(self)
        self.fileMenu = FileMenu(toolbox, activityView)
        self.sectionMenu = SectionMenu()
        self.aboutMenu = AboutMenu()
        self.show()
        self.append(self.fileMenu)
        self.append(self.sectionMenu)
        self.append(self.aboutMenu)

class KSEToolBar(gtk.VBox):
    def __init__(self, activityView):
        gtk.VBox.__init__(self)
        self.show()
        self.activityView = activityView
        self.toolbox = gtk.HBox()
        self.menubar = KSEMenuBar(self.toolbox, activityView)
        self.pack_start(self.menubar)
        self.add(self.toolbox)
        self.toolbox.show()

class KSEPanel(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
        self.show()
        self.set_size_request(125, 100)
        
class GraphicsPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddAtlas = Button("Add atlas", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddState = Button("Add state", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddAnimation = Button("Add animation", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)

class SoundEffectsPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddSound = Button("Add sound", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)
    
class MusicPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddMusic = Button("Add music", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)

class KSETree(gtk.TreeView):
    def __init__(self):
        self.treestore = gtk.TreeStore(str)
        gtk.TreeView.__init__(self, self.treestore)
        self.show()
        self.set_size_request(400, 250)

class KSEStatusView(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        self.logger = logging.getLogger("KRFEditor")
        self.photoshop = Photoshop()
        scrolledWindow = gtk.ScrolledWindow()
        scrolledWindow.add_with_viewport(self.photoshop)
        self.append_page(scrolledWindow, gtk.Label("Photoshop (jk)."))
        self.show_all()

    def openPath(self, filePath):
        try:
            self.photoshop.loadImage(filePath)
            self.photoshop.displayImage()
        except:
            ErrorMessage("Invalid path !")
            self.logger.error("Invalid path submitted to photoshop loading : %s", filePath)

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

    #INTERNAL

    def _addAtlases(self):
        self.atlases = self.tree.findall("atlas")
        print self.atlases
        atlases = gtk.TreeViewColumn()
        cell = gtk.CellRendererText()
        atlases.pack_start(cell, True)
        atlases.add_attribute(cell, "text", 0)
        it = self.model.append(None, ["Atlases"])
        for elem in self.atlases:
            print elem.attrib['name']
            self.model.append(it, [elem.attrib["name"]])
        self.treeview.append_column(atlases)

    def _getAtlasFromPath(self, path):
        return self.atlases[path]

    def _newSelectionCb(self, treeview, path, view_column):
        node = self.sectionCallbacks[path[0]](path[1])
        filePath = None
        print path
        try:
            filePath = node.attrib["path"]
        except KeyError:
            ErrorMessage("No path for this atlas")
        if filePath:
            self.notebook.openPath(filePath)

class Section(gtk.HBox):
    def __init__(self, panel, workzone):
        gtk.HBox.__init__(self)
        self.workzone = workzone
        self.panel = panel
        self.pack_start(self.workzone, True, True, 0)
        self.pack_end(self.panel, False, False, 0)
        self.show()

    def resetTree(self):
        pass
    
    #subclass This
    def createTree(self, section):
        pass

class GraphicSection(Section):
    def __init__(self):
        Section.__init__(self, GraphicsPanel(), KSEGraphicWorkzone())

    def createTree(self, tree):
        self.tree = tree.find("graphics")
        self.workzone.createTree(self.tree)

class KSEActivityView(gtk.Notebook):
    def __init__(self, fileName):
        gtk.Notebook.__init__(self)
        self.show()

        self.xmlHandler = None

        self.graphics = GraphicSection()
#        self.soundeffects = Section(SoundEffectsPanel())
#        self.musics = Section(MusicPanel())

        self.append_page(self.graphics, gtk.Label("Graphics Section"))
#        self.append_page(self.soundeffects, gtk.Label("Sound Effects Section"))
#        self.append_page(self.musics, gtk.Label("Musics Section"))
        if (fileName):
            self.openFile(fileName)
    
    def closeFile(self):
        self.graphics.resetTree()
        self.soundeffects.resetTree()
        self.musics.resetTree()
        self.xmlHandler = None

    def parseAst(self, ast):
        ret = False
        if len(ast.sections) is 1:
            for section in ast.sections[0].sections:
                if section.name == "graphics":
                    self.graphics.createTree(section)
                elif section.name == "sound":
                    for soundSection in section.sections:
                        if soundSection.name == "effects":
                            self.soundeffects.createTree(soundSection)
                        elif soundSection.name == "musics":
                            self.musics.createTree(soundSection)
        return ret

    def openFile(self, fileName):
        userOk = False
        if self.xmlHandler is not None:
            print "Should pop \"do you want to save?\""
        else:
            userOk = True
        if userOk:
            self.xmlHandler = KrfParser(fileName)
            self.graphics.createTree(self.xmlHandler)

class KSEWindow(gobject.GObject):
    def __init__(self, fileName = None, debug = False):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(WINWIDTH, WINHEIGHT)
        self.window.set_title(WINDOWTITLE)
        self.window.set_border_width(BORDERWIDTH)
        
        self.mainbox = gtk.VBox(False, 0)
        self.mainbox.show()
        self.window.add(self.mainbox)
        
        self.activityView = KSEActivityView(fileName)
        self.toolbar = KSEToolBar(self.activityView)
        
        self.mainbox.pack_start(self.toolbar, False, False, 2)
        self.mainbox.pack_start(self.activityView, True, True, 0)

        self.window.connect("delete_event", self.stop)
        self.window.maximize()
        self.window.show()
        self._initLogging(debug)

    def start(self):
        gtk.main()

    def stop(self, event, data = None):
        gtk.main_quit()

    #INTERNAL

    def _initLogging(self, debug):
        self.logger = logging.getLogger("KRFEditor")
        hdlr = logging.FileHandler('/var/tmp/KRFEditor.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        hdlr.setLevel(logging.WARNING)

        if (debug):
            shdlr = logging.StreamHandler()
            self.logger.addHandler(shdlr)
            shdlr.setLevel(logging.INFO)

        self.logger.setLevel(logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="A Kerious Resource File Editor")
    parser.add_argument('-f', action = "store", dest = "fileName", help="specify a file to open")
    parser.add_argument('-d', action = "store_true", default = False, help="Debug boolean")
    return parser.parse_args()

###
# FUNCTIONS
###

if __name__ == "__main__":
    args = parse_args()
    kseWindow = KSEWindow(args.fileName, args.d)
    kseWindow.start()
