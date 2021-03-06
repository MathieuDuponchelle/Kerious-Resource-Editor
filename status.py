import gtk
import gtk.gdk
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

gstSet = True

try:
    from mediafilespreviewer import SimplePreviewWidget
except ImportError:
    gstSet = False

#TODO : subclass this ...
class KSEGraphicView(gtk.VBox):
    """
    Contained by : Workzone
    Status view is quite a bad name for this as we will also be able to
    modify things from here in the future. Displays images, animations or
    music tracks. Contains a Photoshop instance in the case of the graphic view.
    @cvar current : tuple of xmlNode + PILImage for this atlas
    """
    
    ACTION_MOVE = 0
    ACTION_RESIZE = 1 
    
    def __init__(self, instance, panel):
        gtk.VBox.__init__(self)
        self.factory = DrawableFactory()
        self.workzone = instance
        self.logger = logging.getLogger("KRFEditor")
        self.photoshop = Photoshop(self)
        self.panel = panel
        
        vbox = gtk.VBox()
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label("atlas"), False, False, 0)
        self.pack_start(hbox, False, False, 0)
        self.pack_start(self.photoshop, True, True, 0)
        self.atlases = {}
        self.selectedSprites = []
        self.currentAtlas = None
        self.photoshop.connect("button-press-event", self._buttonPressedCb)
        self.photoshop.connect("button-release-event", self._buttonReleaseCb)
        self.photoshop.drawingArea.props.has_tooltip = True
        self.photoshop.drawingArea.connect("query-tooltip", self._queryTooltipCb)

        self.photoshop.eventBox.connect("key-press-event", self._keyPressedCb)
        self.photoshop.eventBox.connect("key-release-event", self._keyReleasedCb)
        
        self.photoshop.drawingArea.drag_dest_set(0, [], 0)
        self.photoshop.drawingArea.connect("motion-notify-event", self._cursorMovedCb);
        
        self.photoshop.drawingArea.set_events(gtk.gdk.EXPOSURE_MASK | gtk.gdk.LEAVE_NOTIFY_MASK |
                                              gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.POINTER_MOTION_MASK |
                                              gtk.gdk.BUTTON_RELEASE_MASK |
                                              gtk.gdk.POINTER_MOTION_HINT_MASK)

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

        self.posLabel = gtk.Label()
        hbox.pack_end(self.posLabel, False, False, 0)

        self.show_all()

        self._setupPopup() #push the funk up
        self.modCtrl = False
        self.modShift = False
        self.selected = None
        
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

            if not node.attrib["width"]: #Imported atlas
                node.attrib["width"] = str(drawable.image.size[0])
                node.attrib["height"] = str(drawable.image.size[1])

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
        entries = [("Edit", self._doSomethingCb, sprite != None),
                   ("Create animation", self._createAnimationCb, len(self.currentAtlas.selection.selected) > 1),
                   ("Add sprite", self._addSpriteCb, True)]

        menu = gtk.Menu()
        for stock_id, callback, sensitivity in entries:
            item = gtk.MenuItem(stock_id)
            if callback:
                item.connect("activate", callback, sprite, event.get_coords())
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
            return True
        sprite = self.photoshop.currentSelection[0]
        if key == "d":
            sprite.texturex += 1
        elif key == "q":
            sprite.texturex -= 1
        elif key == "z":
            sprite.texturey -= 1
        elif key == "s":
            sprite.texturey += 1
        else:
            return False
        sprite.updateXmlNode()
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(sprite)
        self.photoshop.highlightAll(self.currentAtlas)
        return True

    def _atlasChangedCb(self, atlas, sprite):
        self.photoshop.displayImage(atlas.drawable.image)

    def _doSomethingCb(self, menuItem, sprite, event):
        self.editSprite(sprite)
        
    def editSprite(self, sprite):
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
    
    def _buttonReleaseCb(self, widget, evet):
        # Release selected sprite
        if self.selected is not None:
            self.selected.updateXmlNode()
            self.selected = None
            
    # The position taken must be in projected coordinate
    def _updateMousePointer(self, position):
        # We don't want to update mouse pointer is something is selected
        if self.selected is None and self.currentAtlas is not None:
            foundCorner = False
            spriteOver = self.currentAtlas.getSpriteForXY(position[0], position[1])
            
            if spriteOver is not None:
                position[0] -= spriteOver.texturex
                position[1] -= spriteOver.texturey
                
                if spriteOver.isInCorner(position):
                    foundCorner = True
                    self.workzone.app.window.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
                
            if not foundCorner:
                self.workzone.app.window.get_window().set_cursor(gtk.gdk.Cursor(gtk.gdk.ARROW))
    
    def _cursorMovedCb(self, widget, event):
        position = self.photoshop.projectCoords(event.get_coords())
        
        if self.selected is not None:
            
            if self.selectedAction == KSEGraphicView.ACTION_MOVE:
                position[0] -= self.selectedDecal[0]
                position[1] -= self.selectedDecal[1]
                
                self.selected.setPosition(position)
                
                self.refreshDisplay()
                
            elif self.selectedAction == KSEGraphicView.ACTION_RESIZE:
                newDimension = [position[0] - self.selected.texturex, position[1] - self.selected.texturey]
                self.selected.resize(newDimension)
                self.refreshDisplay()
                
            self.panel.updateSelectedSprite(self.selected, self)
        else:
            self._updateMousePointer(position)
            
    def refreshDisplay(self):
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(self.selected)
        self.photoshop.highlightAll(self.currentAtlas)

    def _buttonPressedCb(self, widget, event):
        self.selected = None
        
        self.panel.updateSelectedSprite(None, self)
        # Could happen if no atlas is loaded
        if self.currentAtlas is None:
            return
        
        self.photoshop.drawingArea.grab_focus()
        xoff = self.photoshop.vruler.get_allocation().width
        yoff = self.photoshop.hruler.get_allocation().height
        position = self.photoshop.projectCoords(event.get_coords())
        x = position[0]
        y = position[1]
        sprite = self.currentAtlas.getSpriteForXY(x, y, True)

        #3 == Right click
        if sprite is not None:
            if event.button == 1:
                if self.modShift:
                    self.currentAtlas.selection.addObject(sprite)
                else:
                    if event.type == gtk.gdk.BUTTON_PRESS:
                        self.selected = sprite
                        self.selectedDecal = [x - sprite.texturex, y - sprite.texturey]
                        if sprite.isInCorner(self.selectedDecal):
                            self.selectedAction = KSEGraphicView.ACTION_RESIZE
                        else:
                            self.selectedAction = KSEGraphicView.ACTION_MOVE
                        self.panel.updateSelectedSprite(sprite, self)
                        self.currentAtlas.selection.reset()
                        self.currentAtlas.selection.addObject(sprite)
                    elif event.type == gtk.gdk._2BUTTON_PRESS or event.type == gtk.gdk._3BUTTON_PRESS:
                        self.editSprite(sprite)
            elif event.button == 3:
                self.build_context_menu(event, sprite)
                return
            else:
                # Nothing to do for now
                pass
        else:
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

    def _createAnimationCb(self, widget, sprite, event):
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
        self.currentAtlas.highlightAll()

    def _keyPressedCb(self, widget, event):
        self.photoshop.drawingArea.grab_focus()
        key = gtk.gdk.keyval_name(event.keyval)
        if self._maybeMoveSprite(key):
            return True
        elif key == "Right" or key == "Down":
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(self.currentAtlas.getNextSprite())
            return True
        elif key == "Left" or key == "Up":
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(self.currentAtlas.getPreviousSprite())
            return True
        elif key == "Delete":
            try:
                self.currentAtlas.unreferenceSprite(self.currentAtlas.sprites[self.currentAtlas.currentSprite])
                self.photoshop.highlightAll(self.currentAtlas)
            except IndexError:
                self.currentAtlas.selection.reset()
                return True
            self.currentAtlas.selection.reset()
            self.currentAtlas.selection.addObject(self.currentAtlas.getCurrentSprite())
            return True
        elif key == "Shift_L":
            self.modShift = True
            return True
        elif key == "space":
            self.modCtrl = True
            return True
        return False

    def _keyReleasedCb(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == "Shift_L":
            self.modShift = False
            return True
        elif key == "space":
            self.modCtrl = False
            return True
        return False

    def _addSpriteCb(self, widget, sprite, coords):
        x = coords[0]
        y = coords[1]
        #Coords from the panel
        w = self.workzone.app.activityView.graphics.graphics.width
        h = self.workzone.app.activityView.graphics.graphics.height
        sprite = self.currentAtlas.referenceSprite([w, h, x, y])
        self.currentAtlas.selection.reset()
        self.currentAtlas.selection.addObject(sprite)

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
        if gstSet:
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