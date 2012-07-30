import gtk

IMAGE_ADD="assets/list-add.svg"
IMAGE_NEW="assets/document-new.png"
IMAGE_OPEN="assets/document-open.png"
IMAGE_SAVE="assets/document-save.png"
IMAGE_SAVE_AS="assets/document-save-as.png"

from undo import UndoWrongStateError

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
        
    def addEntry(self, entryName, callBack = None, show = True, accel_group = None):
        item = gtk.ImageMenuItem(entryName)
        if callBack is not None:
            item.connect("activate", callBack)
        self.menu.append(item)
        if show:
            item.show()
        if (accel_group):
            item.set_accel_group(accel_group)
        return item

class KSEMenuBar(gtk.MenuBar):
    def __init__(self, toolbox, activityView, accelGroup):
        gtk.MenuBar.__init__(self)
        self.fileMenu = FileMenu(toolbox, activityView, accelGroup)
        self.sectionMenu = SectionMenu()
        self.aboutMenu = AboutMenu()
        self.show()
        self.append(self.fileMenu)
        self.append(self.sectionMenu)
        self.append(self.aboutMenu)

class KSEToolBar(gtk.VBox):
    def __init__(self, activityView, accelGroup):
        gtk.VBox.__init__(self)
        self.show()
        self.activityView = activityView
        self.toolbox = gtk.HBox()
        self.menubar = KSEMenuBar(self.toolbox, activityView, accelGroup)
        self.pack_start(self.menubar)
        self.add(self.toolbox)
        self.toolbox.show()

class FileMenu(BaseMenu):
    def __init__(self, buttonBox, activityView, accelgroup):
        BaseMenu.__init__(self, "File")
        self.addEntry(gtk.STOCK_NEW, None)
        self.addEntry("gtk-open", self._openProjectCb)
        self.addEntry("gtk-save-as", self._saveProjectAsCb)

        group = gtk.ActionGroup('FileActions')

        action = gtk.Action('Quit', '_Quit me!', 'Quit the Program',
                            gtk.STOCK_QUIT)
        action.set_property('short-label', '_Quit')
        action.connect('activate', gtk.main_quit)
        group.add_action_with_accel(action, None)
        action.set_accel_group(accelgroup)
        action.connect_accelerator()
        item = action.create_menu_item()
        self.menu.append(item)

        action = gtk.Action('Save', '_Save', 'Saves the project',
                            gtk.STOCK_SAVE)
        action.set_property('short-label', '_Save')
        action.connect('activate', self._saveProjectCb)
        group.add_action_with_accel(action, None)
        action.set_accel_group(accelgroup)
        action.connect_accelerator()
        item = action.create_menu_item()
        self.menu.append(item)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_UNDO, gtk.ICON_SIZE_BUTTON)
        button = gtk.Button()
        button.set_image(image)
        buttonBox.pack_start(button, False, False, 0)
        button.show()
        button.connect("clicked", self._undoCb)

        button = gtk.Button()
        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_REDO, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)
        buttonBox.pack_start(button, False, False, 0)
        button.show()
        button.connect("clicked", self._redoCb)

        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_NEW)
        Button(pack=buttonBox, packType=Button.PACKSTART, callBack=self._openProjectCb, imageLink=IMAGE_OPEN)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE)
        Button(pack=buttonBox, packType=Button.PACKSTART, imageLink=IMAGE_SAVE_AS)
        
        self.activityView = activityView

    #INTERNAL

    def _undoCb(self, button):
        try:
            self.activityView.app.action_log.undo()
        except UndoWrongStateError:
            #FIXME : make button insensitive
            print "Nothing to undo anymore"

    def _redoCb(self, button):
        try:
            self.activityView.app.action_log.redo()
        except UndoWrongStateError:
            #FIXME : make button insensitive
            print "Nothing to redo anymore"

    def _openProjectCb(self, fileMenu):
        self.activityView.browse()

    def _saveProjectAsCb(self, fileMenu):
        self.activityView.saveProjectAs()

    def _saveProjectCb(self, fileMenu):
        print "saving"
        self.activityView.saveProject()

    def _exportCb(self, fileMenu):
        self.activityView.export()

    def _buttonClickedCb(self, widget):
        print "clicked"

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