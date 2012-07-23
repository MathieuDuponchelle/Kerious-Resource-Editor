from signallable import Signallable
from loggable import Loggable

class Sprite:
    def __init__(self, path, texturex, texturey, texturew, textureh):
        """
        A sprite is a resource that has been added in an Atlas,
        thus having coordinates in the krf file, relating to its dimensions
        and position in the atlas.
        Width and height are self-explanatory.
        :param path: location of the associated resource.
        """

        self.path = path
        self.texturex = int(texturex)
        self.texturey = int(texturey)
        self.texturew = int(texturew)
        self.textureh = int(textureh)

    