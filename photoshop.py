import gtk
import cairo
import glib
from error import ErrorMessage

class Photoshop(gtk.Image):

    def __init__(self):
        gtk.Image.__init__(self)

    def displayImage(self, path):
        self.path = path
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.path)
        self.set_from_pixbuf(pixbuf)
