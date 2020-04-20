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

# Key binds in the form name : key
keybinds = {"up" : "W", "down" : "S", "left" : "A", "right" : "D", "cw" : "K", "ccw" : "J"}

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
    layouts = {"I" : ((0, 0),(-1, 0),(1, 0),(2, 0)), \
               "J" : ((0, 0),(-1, 0),(1, 0),(-1, -1)), \
               "L" : ((0, 0),(-1, 0),(1, 0),(1, -1)), \
               "O" : ((0, 0),(1, 0),(0, 1),(1, 1)), \
               "S" : ((0, 0),(-1, 0),(0, -1),(1, -1)), \
               "T" : ((0, 0),(-1, 0), (0, -1), (1, 0)), \
               "Z" : ((0, 0),(0, -1),(-1, -1),(1, 0))}

    colors = {"I" : "#42e3f5", "J" : "#3311f2", "L" : "#ff9130", \
              "O" : "#fcde17", "S" : "#54de5b", "T" : "#8e20e8", \
              "Z" : "#eb1c3f"}

    # Pairs of (cos(theta), sin(theta)) for each rotation 0-3
    rot_pairs = ((1, 0),(0, 1),(-1, 0),(0, -1))

    # Sets of kick data sorted by original rotation and then final rotation
    kicks = {0 : \
                {1 : ((0, 0),(-1, 0),(-1, 1),(0, -2),(-1, -2)), \
                 3 : ((0, 0),(1, 0),(1, 1),(0, -2),(1, -2))}, \
             1 : \
                {0 : ((0, 0),(1, 0),(1, -1),(0, 2),(1, 2)), \
                 2 : ((0, 0),(1, 0),(1, -1),(0, 2),(1, 2))}, \
             2 : \
                {1 : ((0, 0),(-1, 0),(-1, 1),(0, -2),(-1, -2)), \
                 3 : ((0, 0),(1, 0),(1, 1),(0, -2),(1, -2))}, \
             3 : \
                {0 : ((0, 0),(-1, 0),(-1, -1),(0, 2),(-1, 2)), \
                 2 : ((0, 0),(-1, 0),(-1, -1),(0, 2),(-1, 2))}}
    
    I_kicks = {0 : \
                {1 : ((0, 0),(-2, 0),(1, 0),(-2, -1),(1, 2)), \
                 3 : ((0, 0),(-1, 0),(2, 0),(-1, 2),(2, -1))}, \
               1 : \
                {0 : ((0, 0),(2, 0),(-1, 0),(2, 1),(-1, -2)), \
                 2 : ((0, 0),(-1, 0),(2, 0),(-1, 2),(2, -1))}, \
               2 : \
                {1 : ((0, 0),(1, 0),(-2, 0),(1, -2),(-2, 1)), \
                 3 : ((0, 0),(2, 0),(-1, 0),(2, 1),(-1, -2))}, \
               3 : \
                {0 : ((0, 0),(1, 0),(-2, 0),(1, -2),(-2, 1)), \
                 2 : ((0, 0),(-2, 0),(1, 0),(-2, -1),(1, 2))}}
    
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
        if self.checkTranslation(dx, dy) == False:
            self.x += dx
            self.y += dy
            for b in self.blocks:
                b.move(b.x + dx, b.y + dy)

    # Returns True if there are any collisions at the (x, y) pairs in new_coords
    def checkRotation(self, new_coords):
        for c in new_coords:
            if self.checkCollision(c[0], c[1]):
                return True

        return False        
    
    def rotate(self, clockwise):
        # Determine old and new rotation state
        old_rot = self.rot
        if clockwise:
            new_rot = self.rot + 1
            if new_rot > 3:
                new_rot = 0
        else:
            new_rot = self.rot - 1
            if new_rot < 0:
                new_rot = 3

        # Get the proper set of kick checks
        if self.type == "O":
            kicks = ((0, 0),(0, 0))
        elif self.type == "I":
            kicks = Tetromino.I_kicks[old_rot][new_rot]
        else:
            kicks = Tetromino.kicks[old_rot][new_rot]

        # Get the corresponding rotation matrix for this rotation
        r = Tetromino.rot_pairs[new_rot]
        
        # Check each (x, y) translation pair in kicks
        for k in kicks:
            
            # New Tetromino coordinates including the kick
            new_x = self.x + k[0]
            new_y = self.y - k[1] # Y coordinate is inverted in kick data
            
            # I and O do not rotate around the "center" of the Tetronimo so they need an extra translation
            if self.type == "I" or self.type == "O":
                if clockwise:
                    new_x += r[1]
                    new_y -= r[0]
                else:
                    new_x -= r[0]
                    new_y -= r[1]

            # Calculate new position of each block accounting for rotation and kick
            new_coords = list()
            
            for i in range(len(self.blocks)):
                b = self.blocks[i]
                l = self.layout[i]
                

                # print("BLOCK "+str(i))
                # print("Layout: ("+str(c[0])+","+str(c[1])+")")
                # print("Rot tuple: ("+str(r[0])+","+str(r[1])+")")
                
                # Calculate positions of blocks using a 2D rotation matrix
                x = new_x + l[0]*r[0] - l[1]*r[1]
                y = new_y + l[0]*r[1] + l[1]*r[0]
                # print("Position: ("+str(x)+","+str(y)+")")

                new_coords.append((x, y)) # Record new position of b

            # Check for collisions at this rotation
            if self.checkRotation(new_coords) == False:
                # If there are no collisions, apply rotation
                self.rot = new_rot
                self.x = new_x
                self.y = new_y
                for i in range(len(self.blocks)):
                    x = new_coords[i][0]
                    y = new_coords[i][1]
                    self.blocks[i].move(x, y)
                return True
        
        return False

    # Moves the Tetromino down until it collides with something
    def drop(self):
        while self.checkTranslation(0, 1) == False:
            self.move(0, 1)
            

class GameController(GameObject):

    def __init__(self):
        GameObject.__init__(self, 1)
        self.counter = 0

        self.t = Tetromino(5, 5, "T")

        self.last_key_state = dict()
    
    def update(self):

        # Get key presses
        key_state = dict()
        key_pressed = dict()
        for key in keybinds.keys():
            key_state[key] = is_pressed(keybinds[key])
            if key_state[key] == True and self.last_key_state.get(key, True) == False:
                key_pressed[key] = True
            else:
                key_pressed[key] = False
            self.last_key_state[key] = key_state[key]

        if key_pressed["up"]:
            self.t.drop()
            self.t = Tetromino(5, 2, "J")
        elif key_pressed["down"]:
            self.t.move(0, 1)
        elif key_pressed["right"]:
            self.t.move(1, 0)
        elif key_pressed["left"]:
            self.t.move(-1, 0)
        elif key_pressed["cw"]:
            self.t.rotate(True) # Rotate clockwise
        elif key_pressed["ccw"]:
            self.t.rotate(False) # Rotate ccw
    

class Background(GraphicsObject):

    color = "white"

    def __init__(self):
        GraphicsObject.__init__(self, base_layer, 0)
        self.r = g.Rectangle(g.Point(0, 0), g.Point(grid_x*grid_size, grid_y*grid_size))
        self.r.setFill(Background.color)
        
        
Grid.init(grid_x, grid_y)
gc = GameController()
bg = Background()
b2 = Block(6, 12)
Game.run()
