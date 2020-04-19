from game import *
from grid import *

block_priority = 0
block_layer = 10
base_layer = 0


class Block(GraphicsObject, GridObject):

    def __init__(self, x, y):
        GraphicsObject.__init__(self, block_layer, block_priority)
        GridObject.__init__(self, x, y)

    def update(self):
        print("Block update")

Grid.init(10, 10)
b = Block(0, 0)
for row in Grid.objects:
    print(row)
b.move(b.x+1, b.y)
for row in Grid.objects:
    print(row)
time.sleep(3)
Game.run()
