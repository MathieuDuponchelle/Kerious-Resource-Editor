import gtk
import logging

from photoshop import Photoshop

class KSEStatusView(gtk.Notebook):
    def __init__(self):
        gtk.Notebook.__init__(self)
        self.logger = logging.getLogger("KRFEditor")
        self.photoshop = Photoshop()
        scrolledWindow = gtk.ScrolledWindow()
        self.eventBox = gtk.EventBox()
        self.eventBox.add(self.photoshop)
        scrolledWindow.add_with_viewport(self.eventBox)
        scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.append_page(scrolledWindow, gtk.Label("Photoshop (jk)."))
        self.show_all()
        self.eventBox.connect("button-release-event", self._keyReleasedCb)

    def openPath(self, node, filePath):
        try:
            self.current = self.photoshop.loadImage(filePath)
            self.logger.info("Image loaded")
            self.photoshop.displayImage(self.current)
            self.logger.info("User opened an atlas : %s", filePath)
        except:
            self.logger.info("Inexistant path submitted to photoshop loading : %s", filePath)
            self.logger.info("Hence creating a new file")
            self.createPath(node, filePath)

    def createPath(self, node, filePath):
        self.current = self.photoshop.createEmptyImage(node.attrib["width"], node.attrib["height"], filePath)
        self.photoshop.displayImage(self.current)

    def mergeResource(self, width, height, path):
        self.photoshop.loadImage(path)
        self.photoshop.mergeImage(width, height, path)
        self.photoshop.displayImage(self.current)

    #INTERNAL

    def _keyReleasedCb(self, widget, event):
        pass