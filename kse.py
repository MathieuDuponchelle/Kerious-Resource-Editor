#!/usr/bin/env python

"""
.. module:: kse
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor:: Mathieu Duponchelle


"""

import sys
import logging
import sys
from xml.etree.ElementTree import Element

from utils import parse_args
from mainwindow import KSEWindow

if __name__ == "__main__":
    args = parse_args()
    kseWindow = KSEWindow(args.fileName, args.debug)
    kseWindow.start()
