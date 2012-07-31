#!/usr/bin/env python

"""
.. module:: kse
   :platform: Unix, Windows
   :synopsis: A useful module indeed.

.. moduleauthor:: Mathieu Duponchelle


"""

from utils import parse_args
from mainwindow import KSEWindow

if __name__ == "__main__":
    args = parse_args()
    kseWindow = KSEWindow(args.fileName, args.debug)
    kseWindow.start()
