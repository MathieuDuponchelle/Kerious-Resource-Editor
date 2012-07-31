# PiTiVi , Non-linear video editor
#
#       pitivi/ui/startupwizard.py
#
# Copyright (c) 2010 Mathieu Duponchelle <seeed@laposte.net>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin St, Fifth Floor,
# Boston, MA 02110-1301, USA.

import os
import gtk

from urllib import unquote

from utils import make_ui_path

class StartUpWizard(object):
    """A Wizard displaying recent projects.

    Allows the user to:
    - create a new project and open the settings dialog (Create button),
    - create a new project with the default settings (dialog close or ESC),
    - load a recently opened project (double click recent chooser),
    - load a project (Browse button),
    - see the quick start manual (User Manual button).
    """

    def __init__(self, app):
        self.app = app
        self.builder = gtk.Builder()
        self.builder.add_from_file(make_ui_path("startupwizard"))
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("window1")
        self.window.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        self.recent_chooser = self.builder.get_object("recentchooser2")
        # FIXME: gtk creates a combo box with only one item, but there is no
        # simple way to hide it.
        filter = gtk.RecentFilter()
        filter.set_name("Projects")
        filter.add_pattern("*.krf")
        self.recent_chooser.add_filter(filter)

    def _newProjectCb(self, unused_button):
        """Handle a click on the New (Project) button."""
        self.app.activityView.newProject()
        self.window.destroy()

    def _loadCb(self, unused_recent_chooser):
        """Handle a double-click on the recent chooser."""
        #FIXME : Do it cleaner
        self.app.activityView.openProject(self._getFileName()[7:])
        self.window.destroy()

    def _getFileName(self):
        """Get the URI of the project selected in the recent chooser."""
        uri = self.recent_chooser.get_current_uri()
        return unquote(uri)

    def _keyPressCb(self, widget, event):
        """Handle a key press event on the dialog."""
        if event.keyval == gtk.keysyms.Escape:
            self.window.destroy()
            self.app.activityView.newProject()

    def _onBrowseButtonClickedCb(self, unused_button6):
        """Handle a click on the Browse button."""
        self.app.activityView.browse(self)

    def _userManualCb(self, unused_button):
        """Handle a click on the Help button."""
        #show_user_manual()
        pass

    def _deleteCb(self, unused_widget, event):
        """Handle a click on the X button of the dialog."""
        self.app.activityView.newProject()

    def show(self):
        self.window.set_transient_for(self.app.window)
        self.window.show()
        self.window.grab_focus()

    def hide(self):
        self.window.hide()
