#game.py

import time

# Static class that keeps track of all game objects and runs update and draw events
class Game:
    
    # Lists of game objects
    objects = list()
    draw_objects = list()
    
    step_time = 1.0/60.0
    
    # Takes one step in the game
    @staticmethod
    def step():
        for o in Game.objects:
            # print("Up@prio: "+str(o.priority))
            o.update()

    # Draws all draw objects
    @staticmethod
    def draw():
        for o in Game.draw_objects:
            # print("Draw@layer: "+str(o.layer))
            o.draw()
    
    # Runs the game
    @staticmethod
    def run():
        while True:
            last_step = time.time()
            Game.step()
            Game.draw()
            time.sleep(max(Game.step_time - (time.time() - last_step), 0))
            # print("FPS: "+str(1.0/(time.time() - last_step)))


# GameObject(priority)
class GameObject(object):

    def __init__(self, priority):
        self.priority = priority

        # Insert self at the correct place in the game objects list
        for i in range(len(Game.objects)):
            if Game.objects[i].priority <= self.priority:
                Game.objects.insert(i, self)
                return
        Game.objects.append(self)

    def getPriority(self):
        return self.priority

    def update(self):
        return


# GaphicsObject(layer, priority)
class GraphicsObject(GameObject):

    def __init__(self, layer, priority):
        GameObject.__init__(self, priority)
        self.layer = layer
        
        # Insert self at the correct place in the draw objects list
        for i in range(len(Game.draw_objects)):
            if Game.draw_objects[i].layer <= self.layer:
                Game.draw_objects.insert(i, self)
                return
        Game.draw_objects.append(self)
        
    def getLayer(self):
        return self.layer

    def draw(self):
        return
