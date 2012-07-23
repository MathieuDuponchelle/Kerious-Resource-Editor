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

class Photoshop(gtk.Image):
    """
    Contained by : KSEStatusView
    """
    def __init__(self):
        gtk.Image.__init__(self)
        self.logger = logging.getLogger("KRFEditor")

    def displayImage(self, drawable):
        pixbuf = Image_to_GdkPixbuf(drawable)
        self.set_from_pixbuf(pixbuf)