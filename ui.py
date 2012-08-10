# -*- coding: utf-8 -*-
# PiTiVi , Non-linear video editor
#
#       pitivi/utils/ui.py
#
# Copyright (c) 2005, Edward Hervey <bilboed@bilboed.com>
# Copyright (c) 2012, Thibault Saunier <thibault.saunier@collabora.com>
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
UI utilities. This file contain the UI constants, and various functions and
classes that help with UI drawing around the application
"""

import gtk
import os
import cairo

from itertools import izip
from urllib import unquote
from gettext import ngettext, gettext as _
from xml.sax.saxutils import escape
from decimal import Decimal

from loggable import doLog, ERROR

# ---------------------- Constants -------------------------------------------#

##
# UI pixels information constants
##
LAYER_HEIGHT_EXPANDED = 50
LAYER_HEIGHT_COLLAPSED = 15
LAYER_SPACING = 15
TRACK_SPACING = 8

SPACING = 6
PADDING = 6

##
#   Drag'n drop constants
##
TYPE_TEXT_PLAIN = 24
TYPE_URI_LIST = 25

# FileSourceFactory (or subclasses)
TYPE_PITIVI_FILESOURCE = 26

# What objects to these correspond to ???
TYPE_PITIVI_EFFECT = 27
TYPE_PITIVI_AUDIO_EFFECT = 28
TYPE_PITIVI_VIDEO_EFFECT = 29
TYPE_PITIVI_AUDIO_TRANSITION = 30
TYPE_PITIVI_VIDEO_TRANSITION = 31

FILE_TUPLE = ("text/plain", 0, TYPE_TEXT_PLAIN)
URI_TUPLE = ("text/uri-list", 0, TYPE_URI_LIST)
FILESOURCE_TUPLE = ("pitivi/file-source", 0, TYPE_PITIVI_FILESOURCE)
EFFECT_TUPLE = ("pitivi/effect", 0, TYPE_PITIVI_EFFECT)
AUDIO_EFFECT_TUPLE = ("pitivi/audio-effect", 0, TYPE_PITIVI_AUDIO_EFFECT)
VIDEO_EFFECT_TUPLE = ("pitivi/video-effect", 0, TYPE_PITIVI_VIDEO_EFFECT)
AUDIO_TRANSITION_TUPLE = ("pitivi/audio-transition", 0, TYPE_PITIVI_AUDIO_TRANSITION)
VIDEO_TRANSITION_TUPLE = ("pitivi/video-transition", 0, TYPE_PITIVI_VIDEO_TRANSITION)


# ---------------------- ARGB color helper-------------------------------------#
def pack_color_32(red, green, blue, alpha=0xFFFF):
    """Packs the specified 16bit color values in a 32bit RGBA value."""
    red = red >> 8
    green = green >> 8
    blue = blue >> 8
    alpha = alpha >> 8
    return (red << 24 | green << 16 | blue << 8 | alpha)


def pack_color_64(red, green, blue, alpha=0xFFFF):
    """Packs the specified 16bit color values in a 64bit RGBA value."""
    return (red << 48 | green << 32 | blue << 16 | alpha)


def unpack_color(value):
    """Unpacks the specified RGBA value into four 16bit color values.

    Args:
      value: A 32bit or 64bit RGBA value.
    """
    if not (value >> 32):
        return unpack_color_32(value)
    else:
        return unpack_color_64(value)


def unpack_color_32(value):
    """Unpacks the specified 32bit RGBA value into four 16bit color values."""
    red = (value >> 24) << 8
    green = ((value >> 16) & 0xFF) << 8
    blue = ((value >> 8) & 0xFF) << 8
    alpha = (value & 0xFF) << 8
    return red, green, blue, alpha


def unpack_color_64(value):
    """Unpacks the specified 64bit RGBA value into four 16bit color values."""
    red = (value >> 48) & 0xFFFF
    green = (value >> 32) & 0xFFFF
    blue = (value >> 16) & 0xFFFF
    alpha = value & 0xFFFF
    return red, green, blue, alpha


def unpack_cairo_pattern(value):
    """Transforms the specified RGBA value into a SolidPattern object."""
    red, green, blue, alpha = unpack_color(value)
    return cairo.SolidPattern(
        red / 65535.0,
        green / 65535.0,
        blue / 65535.0,
        alpha / 65535.0)


def unpack_cairo_gradient(value):
    """Creates a LinearGradient object out of the specified RGBA value."""
    red, green, blue, alpha = unpack_color(value)
    gradient = cairo.LinearGradient(0, 0, 0, 50)
    gradient.add_color_stop_rgba(
        1.0,
        red / 65535.0,
        green / 65535.0,
        blue / 65535.0,
        alpha / 65535.0)
    gradient.add_color_stop_rgba(
        0,
        (red / 65535.0) * 1.5,
        (green / 65535.0) * 1.5,
        (blue / 65535.0) * 1.5,
        alpha / 65535.0)
    return gradient


def hex_to_rgb(value):
    return tuple(float(int(value[i:i + 2], 16)) / 255.0 for i in range(0, 6, 2))


def info_name(info):
    """Return a human-readable filename (without the path and quoting)."""
    return escape(unquote(os.path.basename(info.get_uri())))


def beautify_time_delta(seconds):
    """
    Converts the given time in seconds to a human-readable estimate.

    This is intended for "Unsaved changes" and "Backup file found" dialogs.
    """
    mins = seconds / 60
    sec = int(seconds % 60)
    hours = mins / 60
    mins = int(mins % 60)
    days = int(hours / 24)
    hours = int(hours % 24)

    parts = []
    if days > 0:
        parts.append(ngettext("%d day", "%d days", days) % days)
    if hours > 0:
        parts.append(ngettext("%d hour", "%d hours", hours) % hours)

    if days == 0 and mins > 0:
        parts.append(ngettext("%d minute", "%d minutes", mins) % mins)

    if hours == 0 and mins < 2 and sec:
        parts.append(ngettext("%d second", "%d seconds", sec) % sec)

    return ", ".join(parts)

#--------------------- UI drawing helper -------------------------------------#
# from http://cairographics.org/cookbook/roundedrectangles/
def roundedrec(context, x, y, w, h, r=10):
    "Draw a rounded rectangle"
    #   A****BQ
    #  H      C
    #  *      *
    #  G      D
    #   F****E

    context.move_to(x + r, y)      # Move to A
    context.line_to(x + w - r, y)  # Straight line to B

    # Curve to C, Control points are both at Q
    context.curve_to(x + w, y, x + w, y, x + w, y + r)
    context.line_to(x + w, y + h - r)                               # Move to D
    context.curve_to(x + w, y + h, x + w, y + h, x + w - r, y + h)  # Curve to E
    context.line_to(x + r, y + h)                                   # Line to F
    context.curve_to(x, y + h, x, y + h, x, y + h - r)              # Curve to G
    context.line_to(x, y + r)                                       # Line to H
    context.curve_to(x, y, x, y, x + r, y)                          # Curve to A
    return


#--------------------- Gtk widget helpers ------------------------------------#
def model(columns, data):
    ret = gtk.ListStore(*columns)
    for datum in data:
        ret.append(datum)
    return ret


def set_combo_value(combo, value, default_index=-1):
    model = combo.props.model
    for i, row in enumerate(model):
        if row[1] == value:
            combo.set_active(i)
            return
    combo.set_active(default_index)


def get_combo_value(combo):
    active = combo.get_active()
    return combo.props.model[active][1]

# ---------------------- Classes ---------------------------------------------#
class Point(tuple):

    def __new__(cls, x, y):
        return tuple.__new__(cls, (x, y))

    def __pow__(self, scalar):
        """Returns the scalar multiple self, scalar"""
        return Point(self[0] * scalar, self[1] * scalar)

    def __rpow__(self, scalar):
        """Returns the scalar multiple of self, scalar"""
        return self ** scalar

    def __mul__(self, p2):
        return Point(*(a * b for a, b in izip(self, p2)))

    def __div__(self, other):
        return Point(*(a / b for a, b in izip(self, p2)))

    def __floordiv__(self, scalar):
        """Returns the scalar division of self and scalar"""
        return Point(self[0] / scalar, self[1] / scalar)

    def __add__(self, p2):
        """Returns the 2d vector sum self + p2"""
        return Point(*(a + b for a, b in izip(self, p2)))

    def __sub__(self, p2):
        """Returns the 2-dvector difference self - p2"""
        return Point(*(a - b for a, b in izip(self, p2)))

    def __abs__(self):
        return Point(*(abs(a) for a in self))

    @classmethod
    def from_item_bounds(self, item):
        bounds = item.get_bounds()
        return Point(bounds.x1, bounds.y1), Point(bounds.x2, bounds.y2)

    @classmethod
    def from_widget_bounds(self, widget):
        x1, y1, x2, y2 = widget.get_bounds()
        return Point(x1, y1), Point(x2, y2)
