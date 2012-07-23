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

class Photoshop(gtk.DrawingArea):
    """
    Contained by : KSEStatusView
    """
    def __init__(self):
        gtk.DrawingArea.__init__(self)
        self.logger = logging.getLogger("KRFEditor")
        self.connect("expose-event", self._exposeEventCb)
        self.pixbuf = None
        self.gc = None

    def displayImage(self, drawable):        
        self.set_size_request(drawable.size[0], drawable.size[1])
        pixbuf = Image_to_GdkPixbuf(drawable)
        self.pixbuf = pixbuf
        self.window.draw_pixbuf(None, pixbuf, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)

    def highlight(self, sprite):
        self.gc.set_foreground(self.color)
        self.gc.set_background(self.color)
        self.window.draw_pixbuf(None, self.pixbuf, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)
        self.window.draw_rectangle(self.gc, False, sprite.texturex, sprite.texturey, sprite.texturew, sprite.textureh)

    #INTERNAL

    def _exposeEventCb(self, widget, event):
        if self.gc == None:
            self.gc = self.get_style().fg_gc[gtk.STATE_NORMAL]
            self.color = self.gc.get_colormap().alloc('navajo white')
            self.gc.set_fill(gtk.gdk.SOLID)
            self.gc.set_line_attributes(3, gtk.gdk.LINE_DOUBLE_DASH, gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_ROUND)            
        if self.pixbuf == None:
            return
        self.window.draw_pixbuf(None, self.pixbuf, 0, 0, 0, 0, -1, -1, gtk.gdk.RGB_DITHER_NONE, 0, 0)