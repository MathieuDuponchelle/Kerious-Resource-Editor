# PiTiVi , Non-linear video editor
#
#       configure.py
#
# Copyright (c) 2005, Edward Hervey <bilboed@bilboed.com>
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
"""
Utilities for getting the location of various directories.
Enables identical use for installed and uninstalled versions.
"""

import os.path


def _get_root_dir():
    return '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1])

def _in_devel():
    rd = _get_root_dir()
    return os.path.exists(os.path.join(rd, '.git'))


LIBDIR = '/usr/local/lib'
PKGDATADIR = '/usr/local/share/pitivi'
pitivi_version = '0.15.1'
APPNAME = 'PiTiVi'
APPURL = 'http://www.pitivi.org/'
RELEASES_URL = 'http://pitivi.org/releases.txt'
PYGTK_REQ = '2.17.0'
GTK_REQ = '2.24.0'
PYGST_REQ = '0.10.19'
GST_REQ = '0.10.35'
GNONLIN_REQ = '0.10.16'
PYCAIRO_REQ = '1.0.0'

if _in_devel():
    APPMANUALURL_OFFLINE = 'ghelp://%s' % os.path.join(_get_root_dir(), 'help/C')
else:
    APPMANUALURL_OFFLINE = 'ghelp:pitivi'

APPMANUALURL_ONLINE = 'http://www.pitivi.org/manual'


def get_data_dir():
    if _in_devel():
        datadir = os.path.join(_get_root_dir(), "data")
    elif os.getenv("PITIVI_TOP_LEVEL_DIR"):
        top_level = os.getenv("PITIVI_TOP_LEVEL_DIR")
        datadir = os.path.join(top_level, "data")
    else:
        datadir = PKGDATADIR
    return os.path.abspath(datadir)

def get_pixmap_dir():
    """ Returns the directory for program-only pixmaps """
    return os.path.join(get_data_dir(), 'pixmaps')

def get_ui_dir():
    """ Returns the directory for GtkBuilder/Glade files """
    return os.path.join(get_data_dir(), 'ui')

def get_renderpresets_dir():
    """ Returns the directory for Render Presets files """
    return os.path.join(get_data_dir(), 'renderpresets')

def get_audiopresets_dir():
    """ Returns the directory for Audio Presets files """
    return os.path.join(get_data_dir(), 'audiopresets')

def get_videopresets_dir():
    """ Returns the directory for Video Presets files """
    return os.path.join(get_data_dir(), 'videopresets')
