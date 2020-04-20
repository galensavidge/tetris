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
        self.r = g.Rectangle(g.Point(self.x*grid_size, self.y*grid_size), \
                             g.Point((self.x+1)*grid_size, (self.y+1)*grid_size))
        self.r.setFill("blue")
        self.r.draw(win)

    def update(self):
        return

    def draw(self):
        self.r.move(grid_size*(self.x - self.old_x), grid_size*(self.y - self.old_y))
        self.old_x = self.x
        self.old_y = self.y

    def setColor(self, color):
        self.r.setFill(color)
    
    def delete(self):
        GraphicsObject.delete(self)
        self.r.undraw()


class Tetromino(GameObject):

    # Sets of (x, y) coordinates to build each type of tetromino
    layouts = {"T" : ((0, 0),(-1, 0), (0, -1), (1, 0)), \
               "O" : ((0, 0),(1, 0),(0, 1),(1, 1)), \
               "J" : ((0, 0),(-1, 0),(1, 0),(1, 1))}

    colors = {"T" : "pink", "O" : "yellow", "J" : "blue"}

    # Pairs of (cos(theta), sin(theta)) for each rotation 0-3
    rot_pairs = ((1, 0),(0, 1),(-1, 0),(0, -1))

    
    I_O_rotation_translation = (1, 0)
    
    def __init__(self, x, y, typ):
        GameObject.__init__(self, block_priority)

        # Coordinates
        self.x = x
        self.y = y

        # Number of clockwise rotations from default (0-3)
        self.rot = 0

        # Tetromino type
        self.type = typ

        # Set up Tetromino
        self.layout = Tetromino.layouts[self.type]
        self.blocks = list()
        for coordinate in self.layout:
            b = Block(x+coordinate[0], y+coordinate[1])
            b.setColor(Tetromino.colors[self.type])
            self.blocks.append(b)

    # Checks whether a block from this Tetromino would collide with anything at (x, y)
    def checkCollision(self, x, y):
        # Check that the coordinates are inside the grid
        if Grid.checkBounds(x, y) == False:
            return True

        # Check if there is an object at that space that isn't part of this Tetromino
        o = Grid.getObject(x, y)
        if o is not None and self.blocks.count(o) == 0:
            return True
        else:
            return False
    
    # Returns True if moving by (dx, dy) would collide with a block or the edge of the grid
    def checkTranslation(self, dx, dy):
        for b in self.blocks:
            # Check if b could be moved by (dx, dy)
            new_x = b.x + dx
            new_y = b.y + dy
            if self.checkCollision(new_x, new_y):
                return True

        # Return False once all blocks have been checked
        return False

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        for b in self.blocks:
            b.move(b.x + dx, b.y + dy)

    def rotate(self, rot):
        self.rot = rot
        
        for i in range(len(self.blocks)):
            b = self.blocks[i]
            c = self.layout[i]
            r = Tetromino.rot_pairs[rot]

            # print("BLOCK "+str(i))
            # print("Layout: ("+str(c[0])+","+str(c[1])+")")
            # print("Rot tuple: ("+str(r[0])+","+str(r[1])+")")
            
            # Calculate positions of blocks
            x = self.x + c[0]*r[0] - c[1]*r[1]
            y = self.y + c[0]*r[1] + c[1]*r[0]
            # print("Position: ("+str(x)+","+str(y)+")")

            # I and O do not rotate around the "center" of the Tetronimo so they need an extra translation
            # if self.type == "I" or self.type == "O":
            #    x += r[0]
            #    y += r[1]
            
            b.move(x, y)
            
    
class GameController(GameObject):

    def __init__(self):
        GameObject.__init__(self, 1)
        self.counter = 0

        self.t = Tetromino(5, 5, "J")

        self.last_right = False
        self.last_left = False
    
    def update(self):
        if is_pressed(key_right):
            if self.last_right == False:
                new_rot = self.t.rot + 1
                if new_rot > 3:
                    new_rot = 0
                self.t.rotate(new_rot)
            self.last_right = True
        else:
            self.last_right = False
        
        if is_pressed(key_left):
            new_rot = self.t.rot - 1
            if self.last_left == False:
                if new_rot < 0:
                    new_rot = 3
                self.t.rotate(new_rot)
            self.last_left = True
        else:
            self.last_left = False
    

class Background(GraphicsObject):

    color = "white"

    def __init__(self):
        GraphicsObject.__init__(self, base_layer, 0)
        self.r = g.Rectangle(g.Point(0, 0), g.Point(grid_x*grid_size, grid_y*grid_size))
        self.r.setFill(Background.color)
        
        
Grid.init(grid_x, grid_y)
gc = GameController()
bg = Background()
b2 = Block(1, 5)
Game.run()
