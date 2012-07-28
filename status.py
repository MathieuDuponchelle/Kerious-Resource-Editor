import gtk
import logging
import pango

from photoshop import Photoshop
from atlas import Atlas
from factory import DrawableFactory
from observers import AtlasLogObserver
from sprite import SpriteEditor
from autoDetector import autoSpriteDetector
from detectorSettings import AutoDetectorSettings

#TODO : subclass this ...
class KSEStatusView(gtk.VBox):
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
        self.photoshop.connect("button-press-event", self._keyReleasedCb)
        self.photoshop.drawingArea.props.has_tooltip = True
        self.photoshop.drawingArea.connect("query-tooltip", self._queryTooltipCb)

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

    def _keyReleasedCb(self, widget, event):
        xoff = self.photoshop.vruler.get_allocation().width
        yoff = self.photoshop.hruler.get_allocation().height
        x = event.get_coords()[0] / self.photoshop.zoomRatio - xoff
        y = event.get_coords()[1] / self.photoshop.zoomRatio - yoff
        sprite = self.currentAtlas.getSpriteForXY(x, y, True)
        if event.button == 3:
            self.build_context_menu(event, sprite)
            return
        if self.photoshop.modShift and sprite != None:
            self.currentSprites.append(sprite)
            self.photoshop.highlightSelected(self.currentSprites)
        else:
            self.currentSprites = [sprite]
            self.photoshop.highlight(self.currentAtlas, sprite)
        if sprite == None:
            self.currentSprites = []
            return

    def build_context_menu(self, event, sprite):
        entries = [("Edit", self._doSomethingCb, True),
                   ("Create animation", self._createAnimationCb, len(self.currentSprites) > 1)]

        menu = gtk.Menu()
        for stock_id, callback, sensitivity in entries:
            item = gtk.MenuItem(stock_id)
            if callback:
                item.connect("activate", callback, sprite)
                item.set_sensitive(sensitivity)
                item.show()
                menu.append(item)
        menu.popup(None,None,None,event.button,event.time) 

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
        x = self.currentSprites[0].texturex
        y = self.currentSprites[0].texturey
        tilelen = len(self.currentSprites)
        animw = self.currentSprites[0].texturew
        animh = self.currentSprites[0].textureh
        for sprite in self.currentSprites:
            self.currentAtlas.sprites.remove(sprite)
        self.currentAtlas.referenceAnimation([animw, animh, x, y], tilelen)