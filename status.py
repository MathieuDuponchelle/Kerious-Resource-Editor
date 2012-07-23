import gtk
import logging

from photoshop import Photoshop
from atlas import Atlas
from factory import DrawableFactory
from observers import AtlasLogObserver

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
        self.atlases = {}
        self.currentAtlas = None
        self.eventBox.connect("button-release-event", self._keyReleasedCb)

    def loadAtlasFromXml(self, node, filePath):
        try:
            atlas = self.atlases[filePath]
        except KeyError:
            atlas = Atlas(self.factory)
            atlas.connect("sprite-added", self.workzone._spriteAddedCb)
            atlas.connect("sprite-removed", self._atlasChangedCb)
            atlas.connect("sprite-added", self._atlasChangedCb)
            observer = AtlasLogObserver(self.workzone.app.action_log)
            observer.startObserving(atlas)
            self.atlases[filePath] = atlas
            atlas.loadSprites(node)
            try:
                drawable = self.factory.makeDrawableFromPath(filePath)
                self.logger.info("User opened an atlas : %s", filePath)
            except:
                drawable = self.factory.makeNewDrawable(node.attrib["width"], node.attrib["height"])

            atlas.setDrawable(drawable)
            atlas.setXmlNode(node)
            self.currentAtlas = atlas

        self.photoshop.displayImage(drawable.image)
        self._getOffsetsFromXml(node)

    def mergeResource(self, width, height, path):
        atlas = self.currentAtlas
        if not atlas:
            #TODO : may'be have a default atlas ?
            return
        drawable = self.factory.makeDrawableFromPath(path, width, height)
        coords = atlas.addSprite(drawable.image, path)
        #if no coords, image was not merged, no need to display it again
        if coords:
            self.photoshop.displayImage(atlas.drawable.image)
            coords["xmlNode"] = atlas.xmlNode
            coords["path"] = path
        return coords

    def export(self):
        """
        :param path : path of the image to export
        """
        for atlas in self.atlases:
            self.atlases[atlas].drawable.save()

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
        self.currentAtlas.xoffset = int(xoff)
        self.currentAtlas.yoffset = int(yoff)
        self.currentAtlas.maxOffset = int(maxoff)

    def _keyReleasedCb(self, widget, event):
        self.workzone.getSpriteFromXY(event)

    def _atlasChangedCb(self, atlas, sprite):
        self.photoshop.displayImage(atlas.drawable.image)