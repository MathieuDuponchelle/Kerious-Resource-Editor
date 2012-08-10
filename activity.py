import gtk
import logging

from sections import GraphicSection, SoundSection
from xml.etree.ElementTree import ElementTree
from krfparser import KrfParser
from indent import indent
from error import ErrorMessage

#TODO : connect to "page changed" to change currentSection
class KSEActivityView(gtk.Notebook):
    """
    Contained by : :class: `mainwindow`
    :param fileName: optional string from the arguments.
    :param instance: the :class: KSEWindow
    """
    def __init__(self, fileName, instance):
        self.logger = logging.getLogger("KRFEditor")
        gtk.Notebook.__init__(self)
        self.show()

        self.xmlHandler = None

        self.app = instance
        self.graphics = GraphicSection(self.app)
        self.sounds = SoundSection(self.app)
        self.currentSection = self.graphics

        self.append_page(self.graphics, gtk.Label("Graphics Section"))
        self.append_page(self.sounds, gtk.Label("Sound Section"))

        if fileName:
            self.openProject(fileName)

        self.path = fileName

    def closeFile(self, fileName = None):
        self.graphics.resetTree()
        self.soundeffects.resetTree()
        self.musics.resetTree()
        self.xmlHandler = None

    def newProject(self):
        self.xmlHandler = ElementTree()
        self.xmlHandler.parse("blank/blank.krf")
        self.graphics.createTree(self.xmlHandler)
        self.sounds.createTree(self.xmlHandler)
        self.path = None

    def browse(self, wizard = None):
        chooser = gtk.FileChooserDialog(title="Open project", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.add_pattern("*.krf")
        filter.set_name("Kerious Ressources File (*.krf)")
        chooser.add_filter(filter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.openProject(chooser.get_filename())
            if wizard != None:
                wizard.window.destroy()
        chooser.destroy()

    def openProject(self, fileName):
        userOk = False
        print fileName
        if self.xmlHandler is not None:
            print "Should pop \"do you want to save?\""
        else:
            userOk = True
        if userOk:
            try:
                self.xmlHandler = KrfParser(fileName)
            except IOError:
                ErrorMessage("The file you're trying to open doesn't exist")
                self.logger.error("User tried to open invalid path as a resource file : %s", fileName)
                return
            self.logger.info("User opened a resource file with filename : %s", fileName)
            if self.xmlHandler.isValid():
                self.graphics.createTree(self.xmlHandler)
                self.sounds.createTree(self.xmlHandler)
                self.path = fileName
            else:
                ErrorMessage("The file you opened is not a valid KRF. Begone !")
                self.logger.error("User tried to open an invalid KRF : %s", fileName)


    def saveProjectAs(self):
        chooser = gtk.FileChooserDialog(title="Save project", action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.add_pattern("*.krf")
        filter.set_name("Kerious Ressources File (*.ksf)")
        chooser.add_filter(filter)
        response = chooser.run()
        if response == gtk.RESPONSE_ACCEPT:
            self._doSaveProject(chooser.get_filename())
        chooser.destroy()

    def saveProject(self):
        if self.path == None:
            return self.saveProjectAs()
        self._doSaveProject(self.path)

    def export(self):
        self.currentSection.export()

    #INTERNAL

    def _doSaveProject(self, fileName):
        print fileName
        node = self.xmlHandler.find("graphics")
        indent(node)
        node = self.xmlHandler.find("sounds")
        indent(node)
        self.xmlHandler.write(fileName, encoding="utf-8", xml_declaration=True)
        self.export()