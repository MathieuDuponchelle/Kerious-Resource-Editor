from signallable import Signallable
from loggable import Loggable

class Sprite:
    def __init__(self, path, width, height):
        """
        A sprite is a resource that has been added in an Atlas,
        thus having coordinates in the krf file, relating to its dimensions
        and position in the atlas.
        Width and height are self-explanatory.
        :param path: location of the associated resource.
        """
        self.path = path
        self.width = width
        self.height = height

    def realize(self):
        pass