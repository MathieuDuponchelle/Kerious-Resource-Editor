from undo import UndoableAction

class spriteAdded(UndoableAction):
    def __init__(self, atlas, sprite):
        self.atlas = atlas
        self.sprite = sprite

    def do(self):
        self.atlas.readdSprite(self.sprite)
        self._done()

    def undo(self):
        self.atlas.removeSprite(self.sprite)
        self._undone()

class spriteRemoved(UndoableAction):
    def __init__(self, atlas, sprite):
        self.atlas = atlas
        self.sprite = sprite

    def do(self):
        self.atlas.removeSprite(self.sprite)
        self._done()

    def undo(self):
        self.atlas.readdSprite(self.sprite)
        self._undone()

class AtlasLogObserver(object):
    spriteAddedAction = spriteAdded
    spriteRemovedAction = spriteRemoved
    def __init__(self, log):
        self.log = log

    def startObserving(self, atlas):
        self._connectToAtlas(atlas)

    def stopObserving(self, atlas):
        self._disconnectFromAtlas(atlas)

    def _connectToAtlas(self, atlas):
        atlas.connect("sprite-added", self._spriteAddedCb)
        atlas.connect("sprite-removed", self._spriteRemovedCb)

    def _disconnectFromAtlas(self, atlas):
        atlas.disconnect_by_func(self._spriteAddedCb)
        atlas.disconnect_by_func(self._spriteRemovedCb)

    def _spriteAddedCb(self, atlas, sprite):
        action = self.spriteAddedAction(atlas, sprite)
        self.log.push(action)

    def _spriteRemovedCb(self, atlas, sprite):
        action = self.spriteRemovedAction(atlas, sprite)
        self.log.push(action)