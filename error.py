import gtk
from utils import make_ui_path

class ErrorMessage(gtk.Builder):
    def __init__(self, message = None):
        gtk.Builder.__init__(self)
        self.add_from_file(make_ui_path("error"))
        if message:
            self.get_object("label1").set_text(message)
        self.get_object("button1").connect("clicked", self._destroyCb)

    def _destroyCb(self, unused):
        self.get_object("errordialog").destroy()
