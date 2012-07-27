import gtk
import logging

from sections import GraphicSection
from krfparser import KrfParser
from indent import indent

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
        self.currentSection = self.graphics
#        self.soundeffects = Section(SoundEffectsPanel())
#        self.musics = Section(MusicPanel())

        self.append_page(self.graphics, gtk.Label("Graphics Section"))
#        self.append_page(self.soundeffects, gtk.Label("Sound Effects Section"))
#        self.append_page(self.musics, gtk.Label("Musics Section"))
        if fileName:
            self.openProject(fileName)
        else:
            self.newProject()

        self.path = fileName

    def closeFile(self, fileName = None):
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

    def newProject(self):
        pass

    def openProject(self, fileName):
        userOk = False
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
                self.path = fileName
            else:
                ErrorMessage("The file you opened is not a valid KRF. Begone !")
                self.logger.error("User tried to open an invalid KRF : %s", fileName)

    def saveProjectAs(self, fileName):
        node = self.xmlHandler.find("graphics")
        indent(node)
        self.xmlHandler.write(fileName)

    def saveProject(self):
        if self.path == None:
            return
        node = self.xmlHandler.find("graphics")
        indent(node)
        self.xmlHandler.write(self.path)

    def export(self):
        self.currentSection.export()