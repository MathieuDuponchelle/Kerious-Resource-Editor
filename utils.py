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