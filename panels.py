import gtk

from interface import Button
from utils import get_name_from_uri
from mediafilespreviewer import PreviewWidget

IMAGE_ADD="assets/list-add.svg"
IMAGE_NEW="assets/document-new.png"
IMAGE_OPEN="assets/document-open.png"
IMAGE_SAVE="assets/document-save.png"
IMAGE_SAVE_AS="assets/document-save-as.png"

class KSEPanel(gtk.VBox):
    """ 
    Contained by Sections.
    Panels are on the right-hand side of the UI. They allow addition and
    deletion of resources in their respective sections (for example the
    graphic panel allows adding atlases or resources to these atlases).
    Content will obviously depend on the section.
    """
    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
        self.show()
        self.set_size_request(125, -1)

class GraphicsPanel(KSEPanel):
    """
    This panel contains a treeview listing the image sources for the opened
    project. The model of this treeview is a list of strings :
    [0] -> Name of the resource.
    [1] -> Path of the resource.
    Width and height attributes describe the desired size of the next merge,
    and can be modified from the UI.
    """
    #TODO : handle Aspect Ratio
    #TODO : use gstreamer discoverer to display metadata about the files.
    def __init__(self, instance):
        KSEPanel.__init__(self)
        self.instance = instance
        self.butAddAtlas = Button("Add atlas", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddAnimation = Button("Add animation", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddResource = Button("Add resource image", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddAtlas.connect("clicked", self.instance.addAtlasCb)
        self.butAddResource.connect("clicked", self._addResourcesCb)

        self.model = gtk.ListStore(str, gtk.gdk.Pixbuf, str)
        self.listview = gtk.TreeView()
        self.listview.set_model(self.model)
        scrolledWindow = gtk.ScrolledWindow()
        scrolledWindow.add_with_viewport(self.listview)
        self.pack_start(scrolledWindow, True, True, 0)
        resources = gtk.TreeViewColumn("Resources")
        cell = gtk.CellRendererText()
        resources.pack_start(cell, True)
        resources.add_attribute(cell, "text", 0)
        self.listview.append_column(resources)

        pixbufcol = gtk.TreeViewColumn("Icon")
        pixbufcol.set_expand(False)
        self.listview.append_column(pixbufcol)
        pixcell = gtk.CellRendererPixbuf()
        pixcell.props.xpad = 6
        pixbufcol.pack_start(pixcell)
        pixbufcol.add_attribute(pixcell, 'pixbuf', 1)

        self.listview.connect("row-activated", self.instance.rowActivatedCb, self.model)
        self.width = 32
        self.height = 32
        self._addSpinButton("width : ", self._widthChangedCb)
        self._addSpinButton("height : ", self._heightChangedCb)

        self.show_all()

    def loadProjectResources(self, node):
        """
        @param node: resources/graphics/resources xml Node
        """
        for elem in node.findall("resource"):
            pixbuf = gtk.gdk.pixbuf_new_from_file(elem.attrib["path"])
            pixbuf = pixbuf.scale_simple(64, 64, gtk.gdk.INTERP_BILINEAR)
            self.model.append([elem.attrib["name"], pixbuf, elem.attrib["path"]])

    #INTERNAL

    def _addSpinButton(self, text, function):
        hbox = gtk.HBox()
        hbox.pack_start(gtk.Label(text), False, False, 0)
        adj = gtk.Adjustment(32, 1.0, 102400.0, 1.0, 5.0, 0.0)
        spinbutton = gtk.SpinButton(adj, 0, 0)
        spinbutton.set_wrap(True)
        spinbutton.show()
        spinbutton.connect("value_changed", function)
        hbox.pack_start(spinbutton, True, True, 0)
        hbox.show_all()
        self.pack_end(hbox, False, False, 0)
        spinbutton.connect("button-press-event", self._buttonPressedCb)

    def _widthChangedCb(self, spinner):
        self.width = spinner.get_value()

    def _heightChangedCb(self, spinner):
        self.height = spinner.get_value()

    def _addResourcesCb(self, unused):
        uris = None
        chooser = gtk.FileChooserDialog(title = "Choose location", action = gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        chooser.set_select_multiple(True)
        try:
            pw = PreviewWidget(self.instance.app)
            chooser.set_preview_widget(pw)
            chooser.set_use_preview_label(False)
            chooser.connect('update-preview', pw.add_preview_request)
        except AttributeError:
            print "We must set the pythonpath"
        if chooser.run() == gtk.RESPONSE_ACCEPT:
            uris = chooser.get_filenames()
        chooser.destroy()
        if uris:
            self.instance.addImagesToResources(uris)
            for uri in uris:
                pixbuf = gtk.gdk.pixbuf_new_from_file(uri)
                pixbuf = pixbuf.scale_simple(64, 64, gtk.gdk.INTERP_BILINEAR)
                self.model.append([get_name_from_uri(uri), pixbuf, uri])

    def _buttonPressedCb(self, widget, event):
        widget.grab_focus()

class SoundEffectsPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddSound = Button("Add sound", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)
    
class MusicPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddMusic = Button("Add music", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)
