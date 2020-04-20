# grid.py

# Static class that holds references to grid objects
# Grid.init(w, h) must be called before grid objects can be intitialized
class Grid:

    width = 0
    height = 0
    objects = []
    
    @staticmethod
    def init(width, height):
        Grid.width = width
        Grid.height = height
        Grid.objects = [[None for i in range(width)] for j in range(height)]

    @staticmethod
    def setObject(x, y, obj):
        Grid.objects[y][x] = obj

    @staticmethod
    def getObject(x, y):
        return Grid.objects[y][x]

    @staticmethod
    def checkBounds(x, y):
        return x >= 0 and x < Grid.width and y >= 0 and y < Grid.height

# GridObject(x, y)
class GridObject(object):

    def __init__(self, xpos, ypos):
        self.x = xpos
        self.y = ypos
        self.move(self.x, self.y)

    # Moves the object to another location on the grid
    def move(self, xpos, ypos):
        if Grid.getObject(self.x, self.y) == self:
            Grid.setObject(self.x, self.y, None)
        Grid.setObject(xpos, ypos, self)
        self.x = xpos
        self.y = ypos

# Test code
if __name__ == "__main__":
    Grid.init(3, 2)
    o = GridObject(0, 0)
    for row in Grid.objects:
        print(row)
    o.move(o.x+1, o.y)
    for row in Grid.objects:
        print(row)
