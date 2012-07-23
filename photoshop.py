import gtk
import Image
from error import ErrorMessage
import StringIO
import logging

def Image_to_GdkPixbuf (image):
    file = StringIO.StringIO ()
    image.save (file, 'ppm')
    contents = file.getvalue()
    file.close ()
    loader = gtk.gdk.PixbufLoader ('pnm')
    loader.write (contents, len (contents))
    pixbuf = loader.get_pixbuf()
    loader.close ()
    return pixbuf

class Photoshop(gtk.Image):
    """
    Contained by : KSEStatusView
    """
    def __init__(self):
        gtk.Image.__init__(self)
        self.xoffset = 0
        self.yoffset = 0
        self.maxOffset = 0
        self.images = {}
        self.logger = logging.getLogger("KRFEditor")

    def createEmptyImage(self, width, height, path):
        self.PILImage = Image.new('RGBA', (int(width), int(height)))
        self.images[path] = self.PILImage
        return self.images[path]

    def loadImage(self, path):
        try:
            self.images[path]
            return self.images[path]
        except KeyError:
            pass
        self.path = path
        image = Image.open(path)
        self.images[path] = image
        return self.images[path]

    def displayImage(self, image):
        pixbuf = Image_to_GdkPixbuf(image)
        self.set_from_pixbuf(pixbuf)

    def mergeImage(self, merged, width, height, path):
        image = self.images[path]
        im = image.copy()
        size = width, height
        im.thumbnail(size, Image.ANTIALIAS)
        coords = {}
        if self.xoffset + width > merged.size[0]:
            self.xoffset = 0
            self.yoffset += self.maxOffset
            self.maxOffset = 0
        if self.yoffset > merged.size[1]:
            self.logger.warning("Space in Pixbuf exceeded, NOT ADDING : %s", path)
            return None
        coords["x"] = self.xoffset
        coords["y"] = self.yoffset
        coords["width"] = im.size[0]
        coords["height"] = im.size[1]
        coords["path"] = path
        merged.paste(im, (self.xoffset, self.yoffset))
        self.xoffset += im.size[0]
        if im.size[1] > self.maxOffset:
            self.maxOffset = im.size[1]
        coords["xoff"] = self.xoffset
        coords["yoff"] = self.yoffset
        coords["maxoff"] = self.maxOffset
        self.logger.debug("Space in pixbuf OK, ADDING : %s", path)
        return coords

    def export(self, path, image):
        """
        :param path: path of the image to export
        """
        image.save(path)