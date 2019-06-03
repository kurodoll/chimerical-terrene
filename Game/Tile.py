class Tile:
    def __init__(self, type_):
        self.type = type_
        self.attributes = []

    def setType(self, type_):
        self.type = type_

    def addAttribute(self, attribute):
        self.attributes.append(attribute)
