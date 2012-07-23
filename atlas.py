import gtk
import logging
import os
from xml.etree.ElementTree import Element

from utils import make_ui_path
from signallable import Signallable
from loggable import Loggable
from sprite import Sprite

class Atlas(Signallable, Loggable):
    __signals__ = {
    'sprite-added': ['sprite'],
    'sprite-removed': ['sprite']
    }
    def __init__(self, factory):
        """
        An atlas is a collection of :class: sprites, organized inside it by
        their coordinates and dimensions.
        it to the atlas
        """
        self.drawable = None
        self.width = 0
        self.height = 0
        self.xoffset = 0
        self.yoffset = 0
        self.maxOffset = 0
        self.xmlNode = None
        self.sprites = []
        self.factory = factory

    def setDrawable(self, drawable):
        self.drawable = drawable

    def setXmlNode(self, node):
        self.xmlNode = node

    def addSprite(self, src, path):
        """
        :param src: image to merge
        :param path: Path of the resource.
        """
        dest = self.drawable.image
        coords = {}
        if self.xoffset + src.size[0] > dest.size[0]:
            self.xoffset = 0
            self.yoffset += atlas.maxOffset
            self.maxOffset = 0
        if self.yoffset > dest.size[1]:
            self.logger.warning("Space in Pixbuf exceeded, NOT ADDING : %s", path)
            return None
        coords["x"] = self.xoffset
        coords["y"] = self.yoffset
        coords["width"] = src.size[0]
        coords["height"] = src.size[1]
        sprite = Sprite(path, self.xoffset, self.yoffset, src.size[0], src.size[1])
        dest.paste(src, (self.xoffset, self.yoffset))
        self.xoffset += src.size[0]
        if src.size[1] > self.maxOffset:
            self.maxOffset = src.size[1]
        self._updateXmlNode(sprite)
        #self.logger.debug("Space in pixbuf OK, ADDING : %s", path)
        self.sprites.append(sprite)
        self.emit("sprite-added", sprite)
        return coords
        #sprite = Sprite(path, width, height)

    def removeSprite(self, sprite):
        """
        Will remove the sprite matching the coordinates if existing.
        :param x: X coordinate in the atlas.
        :param y: Y coordinate in the atlas.
        """
        print sprite.texturex, sprite.texturey, sprite.textureh, sprite.texturew
        try:
            self.sprites.remove(sprite)
        except ValueError:
            print "investigate"
        for elem in self.xmlNode.findall("sprite"):
            if elem.attrib["path"] == sprite.path and\
                    elem.attrib["texturex"] == sprite.texturex and \
                    elem.attrib["texturey"] == sprite.texturey:
                self.xmlNode.remove(elem)
        image = self.factory.makeNewDrawable(sprite.texturew, sprite.texturew)
        self.drawable.image.paste(image.image, (sprite.texturex, sprite.texturey))
        self.xoffset = self.xoffset - sprite.texturew
        if self.xoffset < 0:
            self.xoffset = 0
        self.xmlNode.attrib["xoffset"] = str(self.xoffset)
        self.emit("sprite-removed", sprite)

    def readdSprite(self, sprite):
        print sprite.texturew, sprite.textureh
        drawable = self.factory.makeDrawableFromPath(sprite.path, sprite.texturew, sprite.textureh)
        self.addSprite(drawable.image, sprite.path)
        

    def loadSprites(self, node):
        for elem in node.findall("sprite"):
            sprite = Sprite(elem.attrib["path"], elem.attrib["texturex"],
                            elem.attrib["texturey"], elem.attrib["texturew"],
                            elem.attrib["textureh"])
            self.sprites.append(sprite)
            

    def _updateXmlNode(self, sprite):
        self.xmlNode.attrib["xoffset"] = str(self.xoffset)
        self.xmlNode.attrib["yoffset"] = str(self.yoffset)
        self.xmlNode.attrib["maxoffset"] = str(self.maxOffset)
        newNode = Element("sprite", attrib = {"name" : "",
                                              "path" : str(sprite.path),
                                              "texturex" : str(sprite.texturex),
                                              "texturey" : str(sprite.texturey),
                                              "texturew" : str(sprite.texturew),
                                              "textureh" : str(sprite.textureh)})
        self.xmlNode.append(newNode)
        sprite.xmlNode = newNode

class AtlasCreator(gtk.Builder):
    def __init__(self, instance):
        gtk.Builder.__init__(self)
        self.logger = logging.getLogger("KRFEditor")
        self.logger.debug("Atlas Creator opened")
        self.add_from_file(make_ui_path("atlas_creator"))
        self.location = os.getcwd() + "/auto"
        self.app = instance
        self.get_object("assistant1").connect("prepare", self._prepareCb)
        self.get_object("assistant1").connect("apply", self._applyCb)
        self.get_object("assistant1").connect("close", self._closeCb)
        self.get_object("assistant1").connect("delete-event", self._closeCb)
        self.get_object("assistant1").connect("cancel", self._closeCb)
        self.get_object("button1").connect("clicked", self._newFileChooserCb)
        self.get_object("assistant1").set_transient_for(self.app.app.window)

        self.height = 1024
        self.width = 1024

        adj = gtk.Adjustment(1024.0, 1.0, 102400.0, 1.0, 5.0, 0.0)
        spinbutton = gtk.SpinButton(adj, 0, 0)
        spinbutton.set_wrap(True)
        spinbutton.show()
        spinbutton.connect("value_changed", self._widthChangedCb)
        self.get_object("vbox3").pack_end(spinbutton)

        adj = gtk.Adjustment(1024.0, 1.0, 102400.0, 1.0, 5.0, 0.0)
        spinbutton = gtk.SpinButton(adj, 0, 0)
        spinbutton.set_wrap(True)
        spinbutton.show()
        spinbutton.connect("value_changed", self._heightChangedCb)
        self.get_object("vbox3").pack_end(spinbutton)

    # INTERNAL

    def _widthChangedCb(self, spinner):
        self.width = spinner.get_value()

    def _heightChangedCb(self, spinner):
        self.height = spinner.get_value()

    def _newFileChooserCb(self, button):
        chooser = gtk.FileChooserDialog(title = "Choose location", action = gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        if chooser.run() == gtk.RESPONSE_ACCEPT:
            self.location = chooser.get_filename()
            self.logger.info("User chose location %s", self.location)
            button.set_label(self.location)
        # Will pop a warning. Harmless, see http://dev.blankonlinux.or.id/browser/rote/kazam/README?rev=current%3A
        # for example.
        chooser.destroy()
        print self.location

    def _applyCb(self, assistant):
        self.location += ".png"
        self.logger.info("creating new atlas at %s with width = %d and height = %d",
                         self.location, self.width, self.height)
        options = {}
        options["location"] = self.location
        options["width"] = self.width
        options["height"] = self.height
        options["name"] = self.location.split("/")[-1]
        self.app.createAtlas(options)

    def _closeCb(self, assistant, unused = None):
        assistant.destroy()

    def _prepareCb(self, assistant, page):
        assistant.set_page_complete(page, True)
        return True

    def _createAtlasCb(self, unused):
        self.logger.info("Created Atlas")
        self.get_object("dialog").destroy()
