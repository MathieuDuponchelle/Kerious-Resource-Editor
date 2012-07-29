from signallable import Signallable

class Selection(Signallable):
    __signals__ = {
        "selected-changed": []
    }

    def __init__(self):
        self.selected = []

    def addObject(self, obj):
        if obj in self.selected:
            return
        self.selected.append(obj)
        self.emit("selected-changed")

    def removeObject(self, obj):
        if obj not in self.selected:
            return
        self.selected.remove(obj)
        self.emit("selected-changed")

    def isSelected(self, obj):
        if obj in self.selected:
            return True
        return False

    def reset(self):
        self.selected = []
        self.emit("selected-changed")
