#tetris.py

from game import *
from grid import *
import graphics as g
from keyboard import is_pressed

block_priority = 0
block_layer = 10
base_layer = 0

# Graphics init
grid_size = 50 # in px
grid_x = 10
grid_y = 20
win = g.GraphWin("Tetris", grid_x*grid_size, grid_y*grid_size)

# Key binds
key_up = "up"
key_down = "down"
key_left = "left"
key_right = "right"


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
    
    def delete(self):
        GraphicsObject.delete(self)
        self.r.undraw()


class Tetromino(GameObject):

    def __init__(self, x, y):
        GameObject.__init__(self, block_priority)
        self.x = x
        self.y = y
        self.blocks = [Block(x, y), Block(x, y-1), Block(x-1, y), Block(x, y+1)]

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        for b in self.blocks:
            b.move(b.x + dx, b.y + dy)

    # Returns True if moving by (dx, dy) would collide with a block or the edge of the grid
    def checkCollision(self, dx, dy):
        for b in self.blocks:
            new_x = b.x + dx
            new_y = b.y + dy

            # Check that the new coordinates are inside the grid
            if Grid.checkBounds(new_x, new_y) == False:
                return True

            # Check if there is an object at that space that isn't part of this Tetromino
            o = Grid.getObject(new_x, new_y)
            if o is not None and self.blocks.count(o) == 0:
                return True

        # Return False once all blocks have been checked
        return False

class GameController(GameObject):

    def __init__(self):
        GameObject.__init__(self, 1)
        self.b = Block(0, 0)
        self.block_xspeed = 1
        self.counter = 0

        self.t = Tetromino(5, 5)
    
    def update(self):
        if self.b is not None:
            self.counter += 1
            if self.counter >= 30:
                print("("+str(self.b.x)+","+str(self.b.y)+")")
                self.counter = 0
                if self.b.x == grid_x - 1:
                    self.block_xspeed = -1
                elif self.b.x == 0:
                    self.block_xspeed = 1
                self.b.move(self.b.x + self.block_xspeed, self.b.y)

            if is_pressed(key_down):
                self.b.delete()
                self.b = None

        if is_pressed(key_right) and self.t.checkCollision(1, 0) == False:
            self.t.move(1, 0)

        if is_pressed(key_left) and self.t.checkCollision(-1, 0) == False:
            self.t.move(-1, 0)


class Background(GraphicsObject):

    color = "white"

    def __init__(self):
        GraphicsObject.__init__(self, base_layer, 0)
        self.r = g.Rectangle(g.Point(0, 0), g.Point(grid_x*grid_size, grid_y*grid_size))
        self.r.setFill(Background.color)
        
        
Grid.init(10, 10)
gc = GameController()
bg = Background()
b2 = Block(1, 5)
Game.run()
