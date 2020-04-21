# tetris.py

from game import *
from grid import *
import graphics as g
from keyboard import is_pressed
import random


class Tetris:

    # Game
    base_layer = 0
    block_priority = 0
    block_layer = 1
    gc = None

    # Main board
    grid_x = 10
    grid_y = 20
    grid_size = 50 # in px
    board_position_x = 200
    board_position_y = 25
    spawn_x = 5
    spawn_y = 1
    main_board = None

    # GUI
    gui_layer = 2
    gui_priority = 0
    gui = None
    gui_grid_x = 36
    gui_grid_y = 42
    gui_grid_size = 25
    saved_x = 3
    saved_y = 3
    queue_x = 31
    queue_y = 3
    queue_spacing = 6
    gui_board = None

    gui_font = "helvetica"
    
    # Graphics
    window_width = gui_grid_x*gui_grid_size
    window_height = gui_grid_y*gui_grid_size
    win = None
    bg = None
    
    @staticmethod
    def main():
        Tetris.win = g.GraphWin("Tetris", Tetris.window_width, Tetris.window_height)
        Tetris.bg = Background()
        Tetris.main_board = Board(Tetris.grid_x, Tetris.grid_y, \
                                  Tetris.board_position_x, Tetris.board_position_y, \
                                  Tetris.grid_size)
        Tetris.gui = GUI()
        Tetris.gui_board = Board(Tetris.gui_grid_x, Tetris.gui_grid_y, 0, 0, Tetris.gui_grid_size)
        Tetris.gc = GameController()
        Game.run()


# Grid board class
class Board(Grid):

    def __init__(self, width, height, origin_x, origin_y, grid_size):
        Grid.__init__(self, width, height)
        self.x = origin_x
        self.y = origin_y
        self.size = grid_size

    def rowFull(self, row):
        for col in range(self.width):
            if Tetris.main_board.getObject(col, row) is None:
                return False

        return True
    
    def printBoard(self):
        for i in range(self.height):
            for j in range(self.width):
                o = self.getObject(j, i)
                if o is not None:
                    print("~",end="")
                else:
                    print(" ",end="")
            print("")
        print("----------")


# Base block class
class Block(GraphicsObject, GridObject):

    def __init__(self, board, x, y):
        GraphicsObject.__init__(self, Tetris.block_layer, Tetris.block_priority)
        GridObject.__init__(self, board, x, y)
        self.old_x = x
        self.old_y = y
        self.color = "blue" # Default color
        self.drawRectangle()

    def update(self):
        return

    def drawRectangle(self):
        self.r = g.Rectangle(g.Point(self.x*self.grid.size + self.grid.x, \
                                     self.y*self.grid.size + self.grid.y), \
                             g.Point((self.x+1)*self.grid.size + self.grid.x, \
                                     (self.y+1)*self.grid.size + self.grid.y))
        self.r.draw(Tetris.win)
        self.r.setFill(self.color)
        self.r.setWidth(2)
    
    def draw(self):
        if self.x != self.old_x or self.y != self.old_y:
            self.r.move(self.grid.size*(self.x - self.old_x), self.grid.size*(self.y - self.old_y))
            self.old_x = self.x
            self.old_y = self.y

    def changeBoard(self, board, x, y):
        # Change board references
        if self.grid.getObject(self.x, self.y) == self:
            self.grid.setObject(self.x, self.y, None)
        self.grid = board
        self.grid.setObject(x, y, self)

        # Reset position
        self.x = x
        self.y = y
        self.old_x = self.x
        self.old_y = self.y

        # Draw new rectangle
        self.r.undraw()
        self.drawRectangle()
        
    def setColor(self, color):
        self.color = color
        self.r.setFill(color)
    
    def delete(self):
        GraphicsObject.delete(self)
        GridObject.delete(self)
        self.r.undraw()
        del self.r


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
    
    def __init__(self, board, x, y, typ):
        GameObject.__init__(self, Tetris.block_priority)
        self.board = board
        
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
            b = Block(board, x+coordinate[0], y+coordinate[1])
            b.setColor(Tetromino.colors[self.type])
            self.blocks.append(b)

    # Moves the Tetromino to board at position (x, y)
    def spawnOnBoard(self, board, x, y):
        self.board = board
        self.x = x
        self.y = y
        self.rot = 0
        
        for i in range(len(self.blocks)):
            b = self.blocks[i]
            coordinate = self.layout[i]
            b.changeBoard(board, x+coordinate[0], y+coordinate[1])
    
    # Checks whether a block from this Tetromino would collide with anything at (x, y)
    def checkCollision(self, x, y):
        # Check that the coordinates are inside the grid
        if self.board.checkBounds(x, y) == False:
            return True

        # Check if there is an object at that space that isn't part of this Tetromino
        o = self.board.getObject(x, y)
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
            return True
        else:
            return False

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
            
            # I and O do not rotate around the "center" so they need an extra translation
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
                
                # Calculate positions of blocks using a 2D rotation matrix
                x = new_x + l[0]*r[0] - l[1]*r[1]
                y = new_y + l[0]*r[1] + l[1]*r[0]

                # Record new position of b
                new_coords.append((x, y)) 

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

    # Key binds in the form name : key
    keybinds = {"up" : "W", "down" : "S", "left" : "A", "right" : "D", "cw" : "K", "ccw" : "J", \
                "save" : "L", "quit" : "esc"}
    
    # Number of tetrominos to queue on screen
    next_length = 6
    
    def __init__(self):
        GameObject.__init__(self, 10)

        # Game state
        self.state = "playing"
        
        # General game timer
        self.timer = 0
        
        # Timer for automatic drop
        self.drop_timer = 0
        self.drop_timer_duration = 80

        # Timer for placement
        self.place_timer = 0
        self.place_timer_duration = 60

        # The tetromino saved using the save key
        self.saved = None
        self.can_save = True

        # Queue of tetrominos
        self.next = list()

        # Longer queue of tetromino types
        self.next_batch = list()

        # Dictionaries to hold keyboard inputs
        self.key_state = dict()
        self.last_key_state = dict()
        self.key_pressed = dict()

        # Set up tetromino queue and pop first tetromino
        while len(self.next) < GameController.next_length:
            self.enqueueTetromino()
        self.popTetromino()
    
    def update(self):
        # Get key presses
        self.getKeys()

        # Quit the game
        if self.key_pressed["quit"]:
            exit()
        
        if self.state == "playing":
            # Update game timer
            self.timer += 1
            Tetris.gui.setTimer(self.timer//Game.framerate)
            
            # Saving
            if self.key_pressed["save"] and self.can_save:
                self.saveTetromino()
            
            # Translation
            if self.key_pressed["up"]:
                self.t.drop()
                self.placeTetromino()
            elif self.key_pressed["down"]:
                self.t.move(0, 1)
            elif self.key_pressed["right"]:
                self.t.move(1, 0)
            elif self.key_pressed["left"]:
                self.t.move(-1, 0)

            # Rotation
            if self.key_pressed["cw"]:
                if self.t.rotate(True): # Rotate clockwise
                    self.place_timer = 0
            elif self.key_pressed["ccw"]:
                if self.t.rotate(False): # Rotate ccw
                    self.place_timer = 0
            
            # Slowly drop controlled tetromino
            self.drop_timer += 1
            
            if self.drop_timer >= self.drop_timer_duration:
                self.drop_timer = 0
                self.t.move(0, 1)

            # Automatically place controlled tetromino
            if self.t.checkTranslation(0, 1) == True:
                self.place_timer += 1

                if self.place_timer >= self.place_timer_duration:
                    self.place_timer = 0
                    self.placeTetromino()

            else:
                self.place_timer = 0

        elif self.state == "game_over":
            pass
            
    def getKeys(self):
        for key in GameController.keybinds.keys():
            self.key_state[key] = is_pressed(GameController.keybinds[key])
            if self.key_state[key] == True and self.last_key_state.get(key, True) == False:
                self.key_pressed[key] = True
            else:
                self.key_pressed[key] = False
            self.last_key_state[key] = self.key_state[key]
    
    def enqueueTetromino(self):
        # Check if there are any tetrominos left in the last batch
        if len(self.next_batch) == 0:
            # Make a new batch of tetrominos countaing 2x of each type
            types = list(Tetromino.layouts.keys())
            
            for t in types:
                self.next_batch.append(t)
                self.next_batch.append(t)

            random.shuffle(self.next_batch)

        new_type = self.next_batch.pop(0)
        
        self.next.append(Tetromino(Tetris.gui_board, Tetris.queue_x, \
                                   Tetris.queue_y + len(self.next)*Tetris.queue_spacing, new_type))
    
    def popTetromino(self):
        self.t = self.next.pop(0)
        self.t.spawnOnBoard(Tetris.main_board, Tetris.spawn_x, Tetris.spawn_y)

        for t in self.next:
            t.move(0, -1*Tetris.queue_spacing)
        self.enqueueTetromino()
        
        # Reset drop timer
        self.drop_timer = 0

        # Reset save flag
        self.can_save = True

    def saveTetromino(self):
        if self.t is not None:
            if self.saved is None:
                self.saved = self.t
                self.popTetromino()
            else:
                t = self.t
                self.t = self.saved
                self.saved = t
                self.t.spawnOnBoard(Tetris.main_board, Tetris.spawn_x, Tetris.spawn_y)

                # Reset drop timer
                self.drop_timer = 0

                # Set save flag
                self.can_save = False

            self.saved.spawnOnBoard(Tetris.gui_board, Tetris.saved_x, Tetris.saved_y)
        
    def placeTetromino(self):
        # Check if the game is over
        for b in self.t.blocks:
            if b.y <= Tetris.spawn_y:
                Tetris.gui.setGameOver(True)
                self.state = "game_over"
        
        # Check for filled rows
        filled_rows = 0
        
        for y in range(Tetris.grid_y):
            if Tetris.main_board.rowFull(y):
                filled_rows += 1
                
                # Delete objects in this row
                for x in range(Tetris.grid_x):
                    Tetris.main_board.getObject(x, y).delete()

                # Move blocks above this down by one space
                for j in range(y, -1, -1):
                    for x in range(Tetris.grid_x):
                        o = Tetris.main_board.getObject(x, j)
                        if o is not None:
                            Tetris.main_board.getObject(x, j).move(o.x, o.y + 1)
        
        # Take a Tetromino from the queue
        self.popTetromino()

class GUI(GraphicsObject):

    hold_color = "#5c5c5c"
    game_over_color = "red"

    def __init__(self):
        GraphicsObject.__init__(self, Tetris.gui_layer, Tetris.gui_priority)

        # Hold text
        self.hold_t = g.Text(g.Point(Tetris.gui_grid_size*3.5, Tetris.gui_grid_size*6.5), "Hold")
        self.hold_t.setStyle("bold")
        self.hold_t.setFace(Tetris.gui_font)
        self.hold_t.setSize(18)
        self.hold_t.setFill(GUI.hold_color)
        self.hold_t.draw(Tetris.win)

        # Timer text
        self.timer_t = g.Text(g.Point(Tetris.gui_grid_size*3, \
                                      Tetris.gui_grid_size*(Tetris.gui_grid_y - 3)), "0")
        self.timer_t.setStyle("bold")
        self.timer_t.setFace(Tetris.gui_font)
        self.timer_t.setSize(24)
        self.timer_t.setFill(GUI.hold_color)
        self.timer_t.draw(Tetris.win)
        
        # Game over text
        self.game_over_t = g.Text(g.Point(Tetris.window_width/2, Tetris.window_height/2), \
                                  "GAME OVER")
        self.game_over_t.setStyle("bold")
        self.game_over_t.setFace(Tetris.gui_font)
        self.game_over_t.setSize(36)
        self.game_over_t.setFill(GUI.game_over_color)
        self.game_over_drawn = False

    def setTimer(self, seconds):
        self.timer_t.setText(str(seconds))
    
    def setGameOver(self, on):
        if on and self.game_over_drawn == False:
            self.game_over_drawn = True
            self.game_over_t.draw(Tetris.win)
        elif not on and self.game_over_drawn == True:
            self.game_over_drawn = False
            self.game_over_t.undraw(Tetris.win)
            
   
class Background(GraphicsObject):

    color = "white"
    line_color = "grey"

    def __init__(self):
        GraphicsObject.__init__(self, Tetris.base_layer, 0)

        # Draw background color
        self.r = g.Rectangle(g.Point(Tetris.board_position_x, Tetris.board_position_y), \
                             g.Point(Tetris.board_position_x + Tetris.grid_x*Tetris.grid_size, \
                                     Tetris.board_position_y + Tetris.grid_y*Tetris.grid_size))
        self.r.setFill(Background.color)
        self.r.draw(Tetris.win)

        # Draw grid
        for i in range(1, Tetris.grid_x):
            l = g.Line(g.Point(Tetris.board_position_x + Tetris.grid_size*i, \
                               Tetris.board_position_y), \
                       g.Point(Tetris.board_position_x + Tetris.grid_size*i, \
                               Tetris.board_position_y + Tetris.grid_y*Tetris.grid_size))
            l.setOutline(Background.line_color)
            l.draw(Tetris.win)

        for i in range(1, Tetris.grid_y):
            l = g.Line(g.Point(Tetris.board_position_x, \
                               Tetris.board_position_y+ Tetris.grid_size*i), \
                       g.Point(Tetris.board_position_x + Tetris.grid_x*Tetris.grid_size, \
                               Tetris.board_position_y + Tetris.grid_size*i))
            l.setOutline(Background.line_color)
            l.draw(Tetris.win)

    def draw(self):
        # Drawing this every frame prevents the window from not responding
        self.r.setFill(Background.color)


Tetris.main()
