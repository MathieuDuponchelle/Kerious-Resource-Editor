#!/usr/bin/env python

# example textview-basic.py

import gtk
from optionsDialog import OptionsTable
from widgets import NumericWidget

class AutoDetectorSettings:
    def __init__(self, win, detector):
        dialog = gtk.Dialog("Auto Detect Settings",
                            win,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        #window.connect("destroy", self.close_application)
        dialog.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        dialog.set_border_width(0)

        box1 = dialog.get_action_area()
        box1.show()

        box2 = gtk.VBox(False, 10)
        box2.set_border_width(10)
        box1.pack_start(box2, True, True, 0)
        box2.show()

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        textview = gtk.TextView()
        textview.set_justification(gtk.JUSTIFY_CENTER)
        textview.set_editable(False)
        textview.set_cursor_visible(False)
        textview.set_size_request(800, 600)
        textbuffer = textview.get_buffer()
        sw.add(textview)
        sw.show()
        textview.show()

        optionsTable = OptionsTable()

        spinButton = NumericWidget(100, 1, 10)
        spinButton.connectValueChanged(self._intervalChangedCb, None)

        self.combobox = gtk.combo_box_new_text()
        self.combobox.append_text("BaseLine")
        self.combobox.append_text("Centered")
        self.combobox.append_text("Top")
        #Can't get more ugly ..
        self.combobox.set_active_iter(self.combobox.get_model().get_iter_first())

        optionsTable.addOption("Interval : ", spinButton)
        optionsTable.addOption("Color : ", gtk.Entry(), {"activate" : self._colorChangedCb})
        optionsTable.addOption("Match-size : ", gtk.Entry(), {"activate" : self._sizeChangedCb})        
        optionsTable.addOption("Match gravity : ", self.combobox, {"changed" : self._gravityChangedCb})

        optionsTable.setSensitivity("Match gravity : ", False)

        box2.pack_start(sw)
        box2.pack_start(optionsTable)

        buttonBox = gtk.HButtonBox()

        button = gtk.Button("Close")
        buttonBox.pack_start(button, False, False, 0)
        button.connect("clicked", self._closeClickedCb)

        button = gtk.Button("Apply")
        buttonBox.pack_start(button, False, False, 0)
        button.connect("clicked", self._applyClickedCb)

        box2.pack_start(buttonBox)

        infile = open("autoDetect.txt", "r")

        if infile:
            string = infile.read()
            infile.close()
            textbuffer.set_text(string)

        self.interval = 10
        self.color = "black"
        self.matchSize = 0
        self.gravity = None
        self.optionsTable = optionsTable
        self.dialog = dialog
        self.detector = detector

        dialog.show_all()

        #INTERNAL

    def _intervalChangedCb(self, adj, unused):
        self.interval = int(adj.get_value())

    def _colorChangedCb(self, entry):
        self.color = entry.get_text()

    def _sizeChangedCb(self, entry):
        self.matchSize = int(entry.get_text())
        self.gravity = 0
        self.optionsTable.setSensitivity("Match gravity : ", True)        

    def _gravityChangedCb(self, combo):
        self.gravity = combo.get_active()

    def _closeClickedCb(self, unused):
        self.dialog.destroy()

    def _applyClickedCb(self, unused):
        self.detector.setSettings(self.interval, self.color, self.matchSize, self.gravity)
        self.dialog.destroy()

if __name__ == "__main__":
    AutoDetectorSettings(None)
    gtk.main()
