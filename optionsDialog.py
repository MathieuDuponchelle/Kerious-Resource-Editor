import gtk

class OptionsTable(gtk.Table):
    def __init__(self, rows=1, columns=2, homogeneous=True):
        gtk.Table.__init__(self, rows, columns, homogeneous)
        self.set_col_spacing(0, 5)
        self.rows = 1
        self.widgets = {}

    def addOption(self, text, widget, callback=None, show=True):
        self.rows += 1
        self.resize (self.rows, 2)
        label = gtk.Label(text)
        self.attach(label, 0, 1, self.rows - 1, self.rows, yoptions = 0)
        self.attach(widget, 1, 2, self.rows - 1, self.rows, yoptions = 0)
        if show:
            label.show()
            widget.show()
        if callback:
            for elem in callback:
                widget.connect(elem, callback[elem])
        self.widgets[text] = widget

    def setSensitivity(self, text, sensitive):
        try:
            widget = self.widgets[text]
        except KeyError:
            print "No such widget"
            return
        widget.set_sensitive(sensitive)

def printLol(widget):
    print "lol"

if __name__ == "__main__":
    win = gtk.Window()
    table = OptionsTable()
    win.add(table)
    win.show_all()
    table.addOption("dummy", gtk.Button("looooooooooooooooooooooooool"), callback = {"clicked" : printLol})
    table.addOption("dummy2", gtk.Button("loool"))
    table.setSensitivity("dummy", False)
    gtk.main()
