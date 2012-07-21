import gtk

from interface import Button

IMAGE_ADD="assets/list-add.svg"
IMAGE_NEW="assets/document-new.png"
IMAGE_OPEN="assets/document-open.png"
IMAGE_SAVE="assets/document-save.png"
IMAGE_SAVE_AS="assets/document-save-as.png"

class KSEPanel(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self, False, 0)
        self.show()
        self.set_size_request(125, -1)

class GraphicsPanel(KSEPanel):
    def __init__(self, instance):
        KSEPanel.__init__(self)
        self.instance = instance
        self.butAddAtlas = Button("Add atlas", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddState = Button("Add state", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddAnimation = Button("Add animation", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddResource = Button("Add resource image", self, Button.PACKSTART, show=True, imageLink=IMAGE_ADD)
        self.butAddAtlas.connect("clicked", self.instance.addAtlasCb)
        self.butAddResource.connect("clicked", self._addResourcesCb)
        self.model = gtk.ListStore(str, str)
        self.listview = gtk.TreeView()
        self.listview.set_model(self.model)
        self.pack_start(self.listview, True, True, 0)
        self.listview.show()
        resources = gtk.TreeViewColumn("Resources")
        cell = gtk.CellRendererText()
        resources.pack_start(cell, True)
        resources.add_attribute(cell, "text", 0)
        self.listview.append_column(resources)
        self.listview.connect("row-activated", self.instance.rowActivatedCb, self.model)
        self.width = 32
        self.height = 32
        self._addSpinButton("width : ", self._widthChangedCb)
        self._addSpinButton("height : ", self._heightChangedCb)

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

    def _widthChangedCb(self, spinner):
        self.width = spinner.get_value()

    def _heightChangedCb(self, spinner):
        self.height = spinner.get_value()

    def _addResourcesCb(self, unused):
        chooser = gtk.FileChooserDialog(title = "Choose location", action = gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                                   gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        chooser.set_select_multiple(True)
        if chooser.run() == gtk.RESPONSE_ACCEPT:
            self.uris = chooser.get_filenames()
        chooser.destroy()
        for uri in self.uris:
            self.model.append([get_name_from_uri(uri), uri])

class SoundEffectsPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddSound = Button("Add sound", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)
    
class MusicPanel(KSEPanel):
    def __init__(self):
        KSEPanel.__init__(self)
        self.butAddMusic = Button("Add music", self, Button.PACKSTART, True, None, imageLink=IMAGE_ADD)