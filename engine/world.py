class Camera:
    def __init__(self):
        self.x, self.y = 0, 0
    
    def translate(self, dx, dy):
        self.x += dx
        self.y += dy

import pymunk
class World(pymunk.Space):
    def __init__(self, *args, **kwargs):
        pymunk.Space.__init__(self, *args, **kwargs)
        self.iterations = 10
        self.sleep_time_threshold = 0.5
        
        self.add_circle()
        self.add_circle()
        self.add_circle()

    def add_circle(self):
        # add a circle
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, 10)
        body = pymunk.Body(mass, moment)
        body.position = pygame.mouse.get_pos()
        shape = pymunk.Circle(body, 10)
        shape.friction = 0.5
        self.add(body, shape)


import pygame
class Display:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))

    def print_events(self):
        for event in pygame.event.get():
            print(event.type, pygame.event.event_name(event.type))

    def draw(self, world):
        self.screen.fill(pygame.color.THECOLORS["gray"])
        for shape in world.shapes:
            x,y = shape.body.position
            r = 0.5 * shape.area**0.5
            pygame.draw.circle(self.screen, (255, 255, 255), (x,y), r)
        pygame.display.flip()

class Game:
    def __init__(self):
        self.display = Display()
        self.world = World()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16)

        self.running = True
    
    def loop(self):
        self.world.step(0.2)
        self.world.add_circle()
        self.display.draw(self.world)
        self.display.print_events()
        pass

    def run(self):
        while self.running:
            self.loop()

def main():
    g = Game()
    g.run()

if __name__ == "__main__":
    main()