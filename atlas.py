import gtk
from utils import make_ui_path
import logging
from signallable import Signallable
from loggable import Loggable
import os

class Atlas(Signallable, Loggable):
    __signals__ = {
    'sprite-added': ['sprite'],
    'sprite-removed': ['sprite'],
    }
    def __init__(self):
        """
        An atlas is a collection of :class: sprites, organized inside it by
        their coordinates and dimensions.
        it to the atlas
        """
        self.width = 0
        self.height = 0
        self.xoffset = 0
        self.yoffset = 0
        self.maxOffset = 0
        self.sprites = []

    def loadImage(self):
        pass

    def addSprite(self, path, width, height, kar = True):
        """
        Will create and add a sprite to itself and its contained image, at the
        current offset.
        :param path: Path of the resource.
        :param width: Desired width, might vary if kar is True
        :param height: Desired height, might vary if kar is True
        :param kar: boolean, whether to keep the aspect ratio when merging.
        """
        sprite = Sprite(path, width, height)
        self.sprites.append(sprite)
        self.emit("sprite-added", sprite)

    def removeSprite(self, x, y):
        """
        Will remove the sprite matching the coordinates if existing.
        :param x: X coordinate in the atlas.
        :param y: Y coordinate in the atlas.
        """
        self.debug("Trying to remove inexistant sprite %r from atlas %r", sprite, self)
        sprite = None
        self.emit("sprite-removed", sprite)

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
