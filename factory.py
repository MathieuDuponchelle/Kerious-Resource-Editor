import Image

class Drawable:
    def __init__(self):
        self.image = None

    def load(self, path):
        self.path = path
        self.image = Image.open(path)
        self.width = self.image.size[0]
        self.height = self.image.size[1]

    def resize(self, width, height, kar = True):
        drawable = Drawable()
        drawable.image = self.image.copy()
        if kar:
            drawable.image.thumbnail((int(width), int(height)), Image.ANTIALIAS)
        else:
            drawable.image = drawable.image.resize((int(width), int(height)), Image.ANTIALIAS)
        drawable.width = width
        drawable.height = height
        drawable.kar = kar
        drawable.path = self.path
        return drawable

    def new(self, width, height):
        self.image = Image.new('RGBA', (int(width), int(height)))

    def copy(self):
        drawable = Drawable()
        drawable.width = self.width
        drawable.height = self.height
        drawable.path = self.path
        drawable.kar = self.kar
        drawable.image = self.image.copy()
        return drawable

    def matches(self, width, height, kar):
        if self.width == width and self.height == height and self.kar == kar:
            return True
        return False

    def save(self, path=None):
        if path:
            self.image.save(path)
        else:
            self.image.save(self.path)

class DrawableFactory:
    """
    Better code consistency.
    This can also signify drastical differences in performance.
    """
    def __init__(self):
        self.drawables = {}

    def makeDrawableFromPath(self, path, width = None, height = None, kar = True):
        try:
            drawables = self.drawables[path]
            for drawable in drawables:
                if drawable.matches(width, height, kar):
                    return drawable.copy()
            drawable = Drawable()
            drawable.load(path)
        except KeyError:
            drawable = Drawable()
            drawable.load(path)
            self.drawables[path] = []
        self.drawables[path].append(drawable)
        if width and height:
            drawable = drawable.resize(width, height, kar)
            self.drawables[path].append(drawable)
        return drawable

    def makeNewDrawable(self, width, height):
        drawable = Drawable()
        drawable.new(width, height)
        return drawable

if __name__ == "__main__":
    factory = DrawableFactory()
    factory.makeDrawableFromPath("/home/duponc_m/hq.jpg", 32, 32)
    factory.makeDrawableFromPath("/home/duponc_m/hq.jpg", 32, 32)
    factory.makeDrawableFromPath("/home/duponc_m/hq.jpg", 1024, 1024, True)
    im = factory.makeDrawableFromPath("/home/duponc_m/hq.jpg", 1024, 1024, True)
    factory.makeNewDrawable(1024, 242)
    im.save("/home/duponc_m/hqthumb.jpg")
