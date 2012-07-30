import gtk
import logging
import pango

from xml.etree.ElementTree import Element

from photoshop import Photoshop
from atlas import Atlas
from factory import DrawableFactory
from observers import AtlasLogObserver
from sprite import SpriteEditor
from autoDetector import autoSpriteDetector
from detectorSettings import AutoDetectorSettings
from sounds import Sound

from mediafilespreviewer import SimplePreviewWidget

#TODO : subclass this ...
class KSEGraphicView(gtk.VBox):
    """
    Contained by : Workzone
    Status view is quite a bad name for this as we will also be able to
    modify things from here in the future. Displays images, animations or
    music tracks. Contains a Photoshop instance in the case of the graphic view.
    @cvar current : tuple of xmlNode + PILImage for this atlas
    """
    def __init__(self, instance):
        gtk.VBox.__init__(self)
        self.factory = DrawableFactory()
        self.workzone = instance
        self.logger = logging.getLogger("KRFEditor")
        self.photoshop = Photoshop(self)
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("atlas"), False, False, 0)
        self.pack_start(hbox, False, False, 0)
        self.pack_start(self.photoshop, True, True, 0)
        self.atlases = {}
        self.selectedSprites = []
        self.currentAtlas = None
        self.photoshop.connect("button-press-event", self._buttonReleasedCb)
        self.photoshop.drawingArea.props.has_tooltip = True
        self.photoshop.drawingArea.connect("query-tooltip", self._queryTooltipCb)

        self.photoshop.eventBox.connect("key-press-event", self._keyPressedCb)
        self.photoshop.eventBox.connect("key-release-event", self._keyReleasedCb)

        self.detector = autoSpriteDetector()

        button = gtk.ToolButton("gtk-zoom-in")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._zoomInCb)

        button = gtk.ToolButton("gtk-zoom-out")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._zoomOutCb)

        button = gtk.ToolButton("gtk-zoom-fit")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._zoomFitCb)

        button = gtk.ToolButton("gtk-zoom-100")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._zoom100Cb)

        button = gtk.ToolButton("gtk-execute")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._autoDetectSpritesCb)

        button = gtk.ToolButton("gtk-preferences")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._configureDetectorCb)

        button = gtk.ToolButton("gtk-about")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._highlightAllCb)

        button = gtk.ToolButton("gtk-about")
        hbox.pack_end(button, False, False, 0)
        button.connect("clicked", self._highlightAllCb)

        self.posLabel = gtk.Label()
        hbox.pack_end(self.posLabel, False, False, 0)

        self.show_all()

        self._setupPopup() #push the funk up
        self.modCtrl = False
        self.modShift = False

    def loadAtlasFromXml(self, node, filePath):
        try:
            atlas = self.atlases[filePath]
            drawable = atlas.drawable
        except KeyError:
            atlas = Atlas(self.factory)
            atlas.path = filePath
            atlas.connect("sprite-added", self.workzone._spriteAddedCb)
            atlas.connect("sprite-removed", self.workzone._spriteRemovedCb)
            atlas.loadSprites(node)
            atlas.connect("sprite-removed", self._atlasChangedCb)
            atlas.connect("sprite-added", self._atlasChangedCb)
            observer = AtlasLogObserver(self.workzone.app.action_log)
            observer.startObserving(atlas)
            self.atlases[filePath] = atlas
            try:
                drawable = self.factory.makeDrawableFromPath(filePath)
                self.logger.info("User opened an atlas : %s", filePath)
            except:
                drawable = self.factory.makeNewDrawable(node.attrib["width"], node.attrib["height"])

            atlas.setDrawable(drawable)
            atlas.setXmlNode(node)

        self.currentAtlas = atlas
        try:
            atlas.selection.disconnect_by_function(self.photoshop._atlasSelectionChangedCb)
        except Exception:
            pass
        atlas.selection.connect("selected-changed", self.photoshop._atlasSelectionChangedCb)
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
            self.atlases[atlas].drawable.save(self.atlases[atlas].path)

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

    def _setupPopup(self):
        self.popup = gtk.Menu()
        menuItem = gtk.MenuItem("Do something")
        menuItem.connect("activate", self._doSomethingCb)
        self.popup.append(menuItem)

    def _tryAnim(self, x, y, event):
        anim = self.currentAtlas.getAnimForXY(x, y, True)
        if event.button == 3:
            self.build_context_menu(event, anim)
            return
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(anim)

    def build_context_menu(self, event, sprite):
        entries = [("Edit", self._doSomethingCb, True),
                   ("Create animation", self._createAnimationCb, len(self.currentAtlas.selection.selected) > 1)]

        menu = gtk.Menu()
        for stock_id, callback, sensitivity in entries:
            item = gtk.MenuItem(stock_id)
            if callback:
                item.connect("activate", callback, sprite)
                item.set_sensitive(sensitivity)
                item.show()
                menu.append(item)
        menu.popup(None,None,None,event.button,event.time) 

    def _reAlignSprites(self):
        xref = self.currentAtlas.selection.selected[0].texturex
        yref = self.currentAtlas.selection.selected[0].texturey
        wref = self.currentAtlas.selection.selected[0].texturew
        href = self.currentAtlas.selection.selected[0].textureh
        for i, sprite in enumerate(self.currentAtlas.selection.selected[1:]):
            sprite.texturey = yref
            sprite.texturex = xref + (i * wref) 

    def _maybeMoveSprite(self, key):
        if len(self.photoshop.currentSelection) != 1:
            return False
        sprite = self.photoshop.currentSelection[0]
        if key == "Right":
            sprite.texturex += 1
        elif key == "Left":
            sprite.texturex -= 1
        elif key == "Up":
            sprite.texturey -= 1
        elif key == "Down":
            sprite.texturey += 1
        else:
            return False
        sprite.updateXmlNode()
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(sprite)

    def _atlasChangedCb(self, atlas, sprite):
        self.photoshop.displayImage(atlas.drawable.image)

    def _doSomethingCb(self, menuItem, sprite):
        spriteEditor = SpriteEditor(sprite)

    def _queryTooltipCb(self, widget, x, y, mode, tooltip):
        if not self.currentAtlas:
            return False
        x = x / self.photoshop.zoomRatio
        y = y / self.photoshop.zoomRatio
        sprite = self.currentAtlas.getSpriteForXY(x, y)
        if not sprite:
            return False
        if (sprite.path == "NoResource"):
            tooltip.set_text("No resources are associated with this sprite")
            return
        pixbuf = gtk.gdk.pixbuf_new_from_file(sprite.path)
        vbox = gtk.VBox(spacing = 4)
        im = gtk.Image()
        im.set_from_pixbuf(pixbuf)
        vbox.pack_start(im, True, True, 0)
        frame = gtk.Frame()
        label = gtk.Label()
        frame.add(label)
        frame.set_shadow_type(gtk.SHADOW_OUT)
        if not sprite.name:
            label.set_markup("<b><big>Unnamed sprite.</big></b>")
        else:
            label.set_markup("<b><big>" + sprite.name + "</big></b>")
        vbox.pack_start(frame, False, False, 0)
        vbox.show_all()
        tooltip.set_custom(vbox)
        return True

    def _buttonReleasedCb(self, widget, event):
        self.photoshop.drawingArea.grab_focus()
        xoff = self.photoshop.vruler.get_allocation().width
        yoff = self.photoshop.hruler.get_allocation().height
        x = event.get_coords()[0] / self.photoshop.zoomRatio - xoff
        y = event.get_coords()[1] / self.photoshop.zoomRatio - yoff
        sprite = self.currentAtlas.getSpriteForXY(x, y, True)
        if event.button == 3 and sprite != None:
            self.build_context_menu(event, sprite)
            return
        if self.modShift and sprite != None:
            self.currentAtlas.selection.addObject(sprite)
        else:
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(sprite)
        if sprite == None:
            self._tryAnim(x, y, event)
            return

    def _zoomInCb(self, widget):
        self.photoshop.zoomIn()

    def _zoomOutCb(self, widget):
        self.photoshop.zoomOut()

    def _zoomFitCb(self, widget):
        pass

    def _zoom100Cb(self, widget):
        self.photoshop.zoom100()

    def _configureDetectorCb(self, widget):
        AutoDetectorSettings(self.workzone.app.window, self.detector)

    def _autoDetectSpritesCb(self, widget):
        if self.currentAtlas == None:
            return
        self.detector.startDetection(self.currentAtlas.path)
        coordinates = self.detector.getCoordinates()
        self.currentAtlas.sprites = []
        self.currentAtlas.animations = []
        for elem in coordinates:
            self.currentAtlas.referenceSprite(elem)
        if self.detector.gravity != None:
            self.currentAtlas.extendSprites(self.detector.matchSize, self.detector.gravity)
        self.currentAtlas.sortSprites()
        self.photoshop.highlightAll(self.currentAtlas)

    def _highlightAllCb(self, widget):
        self.photoshop.highlightAll(self.currentAtlas)

    def _createAnimationCb(self, widget, sprite):
        self.photoshop.allSelected = False
        self._reAlignSprites()
        x = self.currentAtlas.selection.selected[0].texturex
        y = self.currentAtlas.selection.selected[0].texturey
        tilelen = 0
        animw = self.currentAtlas.selection.selected[0].texturew
        animh = self.currentAtlas.selection.selected[0].textureh
        for sprite in self.currentAtlas.selection.selected:
            try:
                self.currentAtlas.unreferenceSprite(sprite)
                tilelen += 1
            except ValueError:
                continue
        anim = self.currentAtlas.referenceAnimation([animw, animh, x, y], tilelen)
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(anim)

    def _keyPressedCb(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if self.modCtrl:
            return (self._maybeMoveSprite(key))
        elif key == "Right" or key == "Down" and not self.modCtrl:
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(self.currentAtlas.getNextSprite())
            return True
        elif key == "Left" or key == "Up" and not self.modCtrl:
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(self.currentAtlas.getPreviousSprite())
            return True
        elif key == "Delete":
            try:
                self.currentAtlas.sprites.pop(self.currentAtlas.currentSprite)
            except IndexError:
                self.currentAtlas.selection.reset()
                return True
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.add_object(self.currentAtlas.getCurrentSprite())
            return True
        elif key == "Shift_L":
            print "ACTIVATED MOD SHIFT"
            self.modShift = True
            return True
        elif key == "Control_L":
            self.modCtrl = True
            return True
        return False

    def _keyReleasedCb(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Shift_L":
            self.modShift = False
            return True
        elif key == "Control_L":
            self.modCtrl = False
            return True
        return False

class KSESoundView(gtk.VBox):
    def __init__(self, workzone):
        gtk.VBox.__init__(self)
        self.workzone = workzone
        self.xmlNode = None
        self.sounds = {}

    def loadSoundFromXml(self, node, filePath):
        try:
            sound = self.sounds[filePath]
        except KeyError:
            pass
        self.currentSound = sound

    def addSoundWidget(self, elem):
        hbox = gtk.HBox()
        sound = Sound(elem)
        try:
            pw = SimplePreviewWidget(self.workzone.app)
            pw.previewUri("file://" + elem.attrib["path"])
            hbox.pack_start(pw, True, True, 0)
        except AttributeError:
            print "We must set the pythonpath"
        label = gtk.Label(elem.attrib["path"])
        entry = gtk.Entry()
        entry.set_text(elem.attrib["name"])
        entry.connect("activate", self._nameSetCb, elem)
        hbox.pack_end(label, False, False, 0)
        hbox.pack_end(entry, False, False, 0)
        self.pack_start(hbox, False, False, 0)
        pw.show_all()
        self.show_all()

    def _nameSetCb(self, widget, elem):
        elem.attrib["name"] = widget.get_text()

    def addSound(self, uri, name):
        print name, "clop clop"
        newNode = Element("sound", attrib = {"name" : "", "path" : uri})
        self.xmlNode.append(newNode)
        self.addSoundWidget(newNode)

    def loadSounds(self, tree):
        self.xmlNode = tree
        for elem in tree.findall("sound"):
            self.addSoundWidget(elem)