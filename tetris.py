#tetris.py

from game import *
from grid import *
import graphics as g

block_priority = 0
block_layer = 10
base_layer = 0

# Graphics init
grid_size = 50 # in px
grid_x = 10
grid_y = 20
win = g.GraphWin("Tetris", grid_x*grid_size, grid_y*grid_size)

# Base block class
class Block(GraphicsObject, GridObject):

    def __init__(self, x, y):
        GraphicsObject.__init__(self, block_layer, block_priority)
        GridObject.__init__(self, x, y)
        self.old_x = x
        self.old_y = y
        self.color = "blue"
        self.r = g.Rectangle(g.Point(self.x*grid_size, self.y*grid_size), \
                             g.Point((self.x+1)*grid_size, (self.y+1)*grid_size))
        self.r.setFill(self.color)
        self.r.draw(win)

    def update(self):
        return

    def draw(self):
        self.r.move(grid_size*(self.x - self.old_x), grid_size*(self.y - self.old_y))
        self.old_x = self.x
        self.old_y = self.y

    def __del__(self):
        self.r.undraw(win)


class GameController(GameObject):

    def __init__(self):
        GameObject.__init__(self, 1)
        self.b = Block(0, 0)
        self.block_xspeed = 1
        self.counter = 0
        
    def update(self):
        self.counter += 1
        if self.counter >= 30:
            print("("+str(self.b.x)+","+str(self.b.y)+")")
            self.counter = 0
            if self.b.x == grid_x - 1:
                self.block_xspeed = -1
            elif self.b.x == 0:
                self.block_xspeed = 1
            self.b.move(self.b.x + self.block_xspeed, self.b.y)

        
class Background(GraphicsObject):

    color = "white"

    def __init__(self):
        GraphicsObject.__init__(self, base_layer, 0)
        self.r = g.Rectangle(g.Point(0, 0), g.Point(grid_x*grid_size, grid_y*grid_size))
        self.r.setFill(Background.color)
        
        
Grid.init(10, 10)
gc = GameController()
bg = Background()
Game.run()
