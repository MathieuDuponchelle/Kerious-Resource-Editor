import gtk
import logging

from photoshop import Photoshop
from atlas import Atlas
from factory import DrawableFactory

#TODO : subclass this ...
class KSEStatusView(gtk.Notebook):
    """
    Contained by : Workzone
    Status view is quite a bad name for this as we will also be able to
    modify things from here in the future. Displays images, animations or
    music tracks. Contains a Photoshop instance in the case of the graphic view.
    @cvar current : tuple of xmlNode + PILImage for this atlas
    """
    def __init__(self, instance):
        gtk.Notebook.__init__(self)
        self.factory = DrawableFactory()
        self.workzone = instance
        self.logger = logging.getLogger("KRFEditor")
        self.photoshop = Photoshop()
        scrolledWindow = gtk.ScrolledWindow()
        vbox = gtk.VBox()
        self.eventBox = gtk.EventBox()
        self.eventBox.add(self.photoshop)
        scrolledWindow.add_with_viewport(self.eventBox)
        scrolledWindow.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.append_page(scrolledWindow, gtk.Label("Photoshop (jk)."))
        self.show_all()
        self.current = ()
        self.eventBox.connect("button-release-event", self._keyReleasedCb)

    def loadAtlasFromXml(self, node, filePath):
        atlas = Atlas()
        try:
            drawable = self.factory.makeDrawableFromPath(filePath)
            self.current = (node, drawable)
            self.photoshop.displayImage(self.current[1].image)
            self.logger.info("User opened an atlas : %s", filePath)
        except:
            self.logger.info("Inexistant path submitted to photoshop loading : %s", filePath)
            self.logger.info("Hence creating a new file")
            self.createPath(node, filePath)

        self._getOffsetsFromXml(node)

    def createPath(self, node, filePath):
        current = self.photoshop.createEmptyImage(node.attrib["width"], node.attrib["height"], filePath)
        self.current = (node, current)
        self.photoshop.displayImage(self.current[1])

    def mergeResource(self, width, height, path):
        self.photoshop.loadImage(path)
        coords = self.photoshop.mergeImage(self.current[1], int(width), int(height), path)
        #if no coords, image was not merged, no need to display it again
        if coords:
            self.current[0].attrib["xoffset"] = str(coords["xoff"])
            self.current[0].attrib["yoffset"] = str(coords["yoff"])
            self.current[0].attrib["maxoffset"] = str(coords["maxoff"])
            self.photoshop.displayImage(self.current[1])
            coords["xmlNode"] = self.current[0]
        return coords

    def export(self, path):
        """
        :param path : path of the image to export
        """
        self.photoshop.export(path, self.current[1])

    #INTERNAL

    def _getOffsetsFromXml(self, node):
        try:
            xoff = node.attrib["xoffset"]
            yoff = node.attrib["yoffset"]
            maxoff = node.attrib["maxoffset"]
        except KeyError:
            node.attrib["xoffset"] = str(0)
            node.attrib["yoffset"] = str(0)
            node.attrib["maxoffset"] = str(0)
            xoff = 0
            yoff = 0
            maxoff = 0
        self.photoshop.xoffset = int(xoff)
        self.photoshop.yoffset = int(yoff)
        self.photoshop.maxOffset = int(maxoff)

    def _keyReleasedCb(self, widget, event):
        self.workzone.getSpriteFromXY(event)