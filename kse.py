#!/usr/bin/env python

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
