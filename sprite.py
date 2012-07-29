import gtk

from signallable import Signallable
from loggable import Loggable
from utils import make_ui_path

class Sprite:
    def __init__(self, path, texturex, texturey, texturew, textureh):
        """
        A sprite is a resource that has been added in an Atlas,
        thus having coordinates in the krf file, relating to its dimensions
        and position in the atlas.
        Width and height are self-explanatory.
        :param path: location of the associated resource.
        """

        self.path = path
        self.texturex = int(texturex)
        self.texturey = int(texturey)
        self.texturew = int(texturew)
        self.textureh = int(textureh)
        self.name = None
        self.iter = None
        self.xmlNode = None
        self.isAnim = False

    def updateName(self):
        self.xmlNode.attrib["name"] = self.name

    def updateXmlNode(self):
        self.xmlNode.attrib["texturex"] = str(self.texturex)
        self.xmlNode.attrib["texturey"] = str(self.texturey)
        self.xmlNode.attrib["texturew"] = str(self.texturew)
        self.xmlNode.attrib["textureh"] = str(self.textureh)

class Animation(Sprite):
    def __init__(self, path, texturex, texturey, texturew, textureh, tilelen):
        Sprite.__init__(self, path, texturex, texturey, texturew, textureh)
        self.isAnim = True
        self.tilelen = int(tilelen)

    def updateXmlNode(self):
        Sprite.updateXmlNode(self)
        self.xmlNode.attrib["tilelen"] = str(self.tilelen)

class SpriteEditor(gtk.Builder):
    def __init__(self, sprite):
        gtk.Builder.__init__(self)
        self.add_from_file(make_ui_path("sprite_editor"))
        self.sprite = sprite
        if sprite.name:
            self.get_object("entry1").set_text(sprite.name)
        self.get_object("button2").connect("clicked", self._applyCb)
        self.get_object("button1").connect("clicked", self._cancelCb)

    #INTERNAL

    def _applyCb(self, widget):
        self.sprite.name = self.get_object("entry1").get_text()
        self.sprite.updateName()
        self.get_object("dialog1").destroy()

    def _cancelCb(self, widget):
        self.get_object("dialog1").destroy()