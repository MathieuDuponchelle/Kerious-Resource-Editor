import argparse

UI_PATH = "ui"
NAME_LENGTH = 40

def make_ui_path(fileName):
    return UI_PATH + "/" + fileName + ".ui"

def get_name_from_uri(uri):
    return uri.split("/")[-1][0:NAME_LENGTH]

def parse_args():
    parser = argparse.ArgumentParser(description="A Kerious Resource File Editor")
    parser.add_argument('-f', action = "store", dest = "fileName", help="specify a file to open")
    parser.add_argument('-d', action = "store", dest = "debug", help="Debug level on stderr")
    return parser.parse_args()

def is_contained_by(x, y, refX, refY, refW, refH):
    """
    :param x: x value of a point
    :param y: y value of that point
    :param refX: x of the top left corner of a surface
    :param refY: y of the top left corner of that surface
    :param refW: width of that surface
    :param refH: height of that surface
    :returns: a bool
    """
    if x < refX or x >= refX + refW:
        return False
    if y < refY or y >= refY + refH:
        return False
    return True