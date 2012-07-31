import gtk
import Image
from error import ErrorMessage
import StringIO
import logging

def Image_to_GdkPixbuf (image):
    file = StringIO.StringIO ()
    image.save (file, 'ppm')
    contents = file.getvalue()
    file.close ()
    loader = gtk.gdk.PixbufLoader ('pnm')
    loader.write (contents, len (contents))
    pixbuf = loader.get_pixbuf()
    loader.close ()
    return pixbuf

class Photoshop(gtk.ScrolledWindow):
    """
    Contained by : KSEStatusView
    """
    def __init__(self, status):
        gtk.ScrolledWindow.__init__(self)
        self.logger = logging.getLogger("KRFEditor")

        self.status = status

        self.table = gtk.Table()
        self.add_with_viewport(self.table)
        eventBox = gtk.EventBox()
        self.drawingArea = gtk.DrawingArea()
        self.drawingArea.connect("expose-event", self._exposeEventCb)
        self.drawingArea.set_flags(gtk.CAN_FOCUS)
        eventBox.add(self.drawingArea)
        self.table.attach(eventBox, 1, 2, 1, 2, gtk.FILL, gtk.FILL)

        self.hruler = gtk.HRuler()
        self.vruler = gtk.VRuler()
        self.table.attach(self.hruler, 1, 2, 0, 1, gtk.EXPAND | gtk.FILL, gtk.FILL)
        self.table.attach(self.vruler, 0, 1, 1, 2, gtk.FILL, gtk.EXPAND | gtk.FILL)

        self.drawingArea.connect_object("motion-notify-event", self._motionNotifyCb, self.hruler)
        self.drawingArea.connect_object("motion-notify-event", self._motionNotifyCb, self.vruler)

        self.eventBox = eventBox
        self.pixbuf = None
        self.gc = None
        self.highlightedSprites = None
        self.highlightedAnimations = None
        self.allHighlighted = False
        self.zoomRatio = 1.0

        self.modShift = False
        self.modCtrl = False
        self.currentSelection = None

        self.show_all()

    def displayImage(self, drawable):
        self.drawingArea.set_size_request(drawable.size[0], drawable.size[1])
        pixbuf = Image_to_GdkPixbuf(drawable)
        self.pixbuf = pixbuf
        self.originalPixbuf = self.pixbuf
        self.drawable = drawable
        self._drawImage()

    def highlight(self, sprite, selected):
        if sprite == None:
            return
        if selected and not sprite.isAnim:
            color = self.gc.get_colormap().alloc('blue')
        elif selected:
            color = self.gc.get_colormap().alloc('red')
        else:
            color = self.gc.get_colormap().alloc('LimeGreen')
        self.gc.set_foreground(color)   
        if not sprite.isAnim:
            self.drawingArea.window.draw_rectangle(self.gc, False, int(sprite.texturex * self.zoomRatio),
                                                   int(sprite.texturey * self.zoomRatio),
                                                   int(sprite.texturew * self.zoomRatio),
                                                   int(sprite.textureh * self.zoomRatio))
        elif sprite != None:
            self.drawingArea.window.draw_rectangle(self.gc, False, int(sprite.texturex * self.zoomRatio),
                                                   int(sprite.texturey * self.zoomRatio),
                                                   int(sprite.texturew * sprite.tilelen * self.zoomRatio),
                                                   int(sprite.textureh * self.zoomRatio))
        color = self.gc.get_colormap().alloc('black')
        self.gc.set_foreground(color)

    def highlightAll(self, atlas):
        self._drawImage()
        self.highlightedSprites = atlas.sprites
        self.highlightedAnimations = atlas.animations
        self.allHighlighted = True
        for elem in atlas.sprites:
            self.highlight(elem, False)
        for elem in atlas.animations:
            self.highlight(elem, False)
        if self.currentSelection:
            for elem in self.currentSelection:
                self.highlight(elem, True)

    def zoomIn(self):
        self.zoomRatio += 0.5
        self.pixbuf = self.originalPixbuf.scale_simple(int(self.originalPixbuf.props.width * self.zoomRatio),
                                                       int(self.originalPixbuf.props.height * self.zoomRatio),
                                                       gtk.gdk.INTERP_HYPER)
        self._drawImage()

    def zoomOut(self):
        self._cleanDrawingArea()
        self.zoomRatio *= 0.5
        self.pixbuf = self.originalPixbuf.scale_simple(int(self.originalPixbuf.props.width * self.zoomRatio),
                                                       int(self.originalPixbuf.props.height * self.zoomRatio),
                                                       gtk.gdk.INTERP_HYPER)
        self._drawImage()

    def zoom100(self):
        self._cleanDrawingArea()
        self.zoomRatio = 1.0
        self.pixbuf = self.originalPixbuf
        self._drawImage()

    #INTERNAL

    def _cleanDrawingArea(self):
        color = self.gc.get_colormap().alloc('white')
        self.gc.set_foreground(color)
        self.drawingArea.window.draw_rectangle(self.gc, True, 0, 0, self.drawingArea.get_allocation().width, self.drawingArea.get_allocation().height)
        color = self.gc.get_colormap().alloc('black')
        self.gc.set_foreground(color)

    def _drawImage(self):
        self.drawingArea.set_size_request(int(self.zoomRatio * self.drawable.size[0]), int(self.zoomRatio * self.drawable.size[1]))
        self.drawingArea.window.draw_pixbuf(None, self.pixbuf, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        xsize = self.drawable.size[0] if self.drawable.size[0] > self.drawingArea.get_allocation().width else self.drawingArea.get_allocation().width
        ysize = self.drawable.size[1] if self.drawable.size[1] > self.drawingArea.get_allocation().height else self.drawingArea.get_allocation().height
        self.hruler.set_range(0.0, float(xsize / self.zoomRatio), 0.0, float(self.drawable.size[0] / self.zoomRatio))
        self.vruler.set_range(0.0, float(ysize / self.zoomRatio), 0.0, float(self.drawable.size[1] / self.zoomRatio))

    def _exposeEventCb(self, widget, event):
        #First, draw the atlas itself

        if self.gc == None:
            self.gc = self.get_style().fg_gc[gtk.STATE_NORMAL]
            self.color = self.gc.get_colormap().alloc('LimeGreen')
            self.gc.set_fill(gtk.gdk.SOLID)
            self.gc.set_line_attributes(3, 0, gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_ROUND)            
        if self.pixbuf == None:
            return
        self._drawImage()

        #Then, redraw highlighted sprites
        
        if self.allHighlighted:
            self.highlightAll(self.status.currentAtlas)
        elif self.currentSelection:
            for elem in self.currentSelection:
                self.highlight(elem, True)

    def _motionNotifyCb(self, ruler, event):
        coords = event.get_coords()
        self.status.posLabel.set_text(str(coords[0] / self.zoomRatio) + "," + str(coords[1] / self.zoomRatio))
        ruler.emit("motion-notify-event", event)

    def _atlasSelectionChangedCb(self, selection):
        if not self.allHighlighted:
            self._drawImage()
        elif self.currentSelection is not None:
            for elem in self.currentSelection:
                self.highlight(elem, False)

        self.currentSelection = selection.selected
        for elem in self.currentSelection:
            self.highlight(elem, True)