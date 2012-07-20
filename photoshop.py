import gtk
import cairo
import glib
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

class Photoshop(gtk.Image):
    def __init__(self):
        gtk.Image.__init__(self)

    def loadImage(self, path):
        self.path = path
        self.PILImage = Image.open(path)

    def displayImage(self):
        pixbuf = Image_to_GdkPixbuf(self.PILImage)
        self.set_from_pixbuf(pixbuf)

    
