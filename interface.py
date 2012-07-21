import gtk

IMAGE_ADD="assets/list-add.svg"
IMAGE_NEW="assets/document-new.png"
IMAGE_OPEN="assets/document-open.png"
IMAGE_SAVE="assets/document-save.png"
IMAGE_SAVE_AS="assets/document-save-as.png"

class Button(gtk.Button):
    FILL = 0
    PACKSTART = 1
    PACKEND = 2
    
    def __init__(self, name = None, pack = None, packType = None, show = True, callBack = None, imageLink = None):        
        gtk.Button.__init__(self)
        self.constructButton(name, imageLink)
        if packType is None:
            packType = Button.FILL
        if pack is not None:
            if packType == Button.FILL:
                pack.add(self)
            elif packType == Button.PACKSTART:
                pack.pack_start(self, False, False, 0)
            elif packType == Button.PACKEND:
                pack.pack_end(self, False, False)
            else:
                print "Button Error : Invalid packType", packType
        if callBack is not None:
            self.connect("clicked", callBack)
        if show:
            self.show()
            
    def constructButton(self, name, imageLink):
        nameLabel = None
        image = None
        if name is not None:
            nameLabel = gtk.Label(name)
            nameLabel.show()
        if imageLink is not None:
            image = gtk.Image()
            image.set_from_file(imageLink)
            image.show()
        if nameLabel is not None and image is not None:
            box = gtk.HBox()
            box.show()
            box.pack_start(image, False, False)
            box.add(nameLabel)
            self.add(box)
        elif nameLabel is not None:
            self.add(nameLabel)
        elif image is not None:
            self.add(image)

class BaseMenu(gtk.MenuItem):
    def __init__(self, menuName):
        gtk.MenuItem.__init__(self, menuName)
        self.menu = gtk.Menu()
        self.set_submenu(self.menu)
        self.show()
        
    def addEntry(self, entryName, callBack = None, show = True):
        item = gtk.MenuItem(entryName)
        if callBack is not None:
            item.connect("activate", callBack)
        self.menu.append(item)
        if show:
            item.show()

class KSEMenuBar(gtk.MenuBar):
    def __init__(self, toolbox, activityView):
        gtk.MenuBar.__init__(self)
        self.fileMenu = FileMenu(toolbox, activityView)
        self.sectionMenu = SectionMenu()
        self.aboutMenu = AboutMenu()
        self.show()
        self.append(self.fileMenu)
        self.append(self.sectionMenu)
        self.append(self.aboutMenu)

class KSEToolBar(gtk.VBox):
    def __init__(self, activityView):
        gtk.VBox.__init__(self)
        self.show()
        self.activityView = activityView
        self.toolbox = gtk.HBox()
        self.menubar = KSEMenuBar(self.toolbox, activityView)
        self.pack_start(self.menubar)
        self.add(self.toolbox)
        self.toolbox.show()

class FileMenu(BaseMenu):
    def __init__(self, buttonBox, activityView):
        BaseMenu.__init__(self, "File")
        self.addEntry("New", None)
        self.addEntry("Open", self.openFileAction)
        self.addEntry("Save", None)
        self.addEntry("Save As...", None)
        self.addEntry("Quit", None)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_NEW)
        Button(pack=buttonBox, packType=Button.PACKSTART, callBack=self.openFileAction, imageLink=IMAGE_OPEN)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE_AS)
        
        self.activityView = activityView
        
    def openFileAction(self, fileMenu):
        chooser = gtk.FileChooserDialog(title="Choose your file", action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.add_pattern("*.krf")
        filter.set_name("Kerious Ressources File (*.ksf)")
        chooser.add_filter(filter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.activityView.openFile(chooser.get_filename())
        chooser.destroy()
    
class SectionMenu(BaseMenu):
    def __init__(self):
        BaseMenu.__init__(self, "Sections")
        self.addEntry("Graphics", None)
        self.addEntry("Sound Effects", None)
        self.addEntry("Musics", None)
        
class AboutMenu(BaseMenu):
    def __init__(self):
        BaseMenu.__init__(self, "Infos")
        self.addEntry("About Kerious", None)
        self.addEntry("About Kerious Ressources Editor", None)