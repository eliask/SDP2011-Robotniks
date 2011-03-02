"""
In this example, I'm going to show you how easy it is to integrate the gui into
your already made game. Also demonstrates linking custom functions (very cool,
be sure to see)!
"""

import sys
sys.path.insert(0, "..")
import random

import pygame
import gooeypy as gui
from gooeypy.const import *

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 480))
myguiapp = gui.Container(width=640, height=100,
        surface=pygame.surface.Surface((640, 100), pygame.SRCALPHA))


# Lets create a very simple game where you move around an image.
image = pygame.image.load("image.png").convert_alpha()
x = 200
y = 250


tb = gui.TextBlock(value="This example is for demonstrating how you can easily use GooeyPy in your already made game.", align="center", y=20, width=350)


def get_data():
    # We are going to set this function to be the value of the TextBlock widget,
    # (i.e. link it). Because GooeyPy doesn't know when x or y changes, it will
    # call this function every tick. It will still only update it's widgets when
    # it has to though. :)
    return "Current pie position: %s, %s" % (x,y)
# Remeber that when you pass a function as a value to pass a refrence of the
# function and not call it (as that would assign the vaues, not the actual
# function). This works not only with the value field but with all the
# styling options as well, such as x, y, width, height and the list goes on...
# see docs for full list of style options.
l = gui.Label(get_data, align="center", y=70, font_size=25, color=(255,255,255))

# crab.gif is a color key. This demonstrates that GooeyPy uses it.
crab_input = gui.Input(width=100, bgimage="crab.gif")

myguiapp.add(tb, crab_input, l)

# In your game you will probably have more than one gui area. Let's create a
# second app and call it game_panel.
game_panel = gui.Container(x=40, y=130,
    surface=pygame.surface.Surface((180,50), pygame.SRCALPHA))

button = gui.Button("Some button")
game_panel.add(button)

tick_count = 0
while True:
    clock.tick(40)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            sys.exit()

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()

    k = pygame.key.get_pressed()
    if k[K_RIGHT]:
        x += 5
    if k[K_LEFT]:
        x -= 5
    if k[K_DOWN]:
        y += 5
    if k[K_UP]:
        y -= 5
    x = max(0, min(x, 460))
    y = max(100, min(y, 360))

    screen.fill((0,0,0))

    myguiapp.run(events)
    game_panel.run(events)

    # If you want the gui to be drawn to the screen every time, you
    # can set "myguiapp.dirty = True" before calling app.draw()
    myguiapp.draw()
    game_panel.dirty = True
    game_panel.draw()

    # With updating the display you have a few options. If you want to flip the
    # entire screen, you can simply do:
    # pygame.display.flip()
    # Or if you are wanting to just update the parts the screen that need to be
    # updated, you can do something like this:

    # In your game, add the rects of the screen that need updating to this list.
    myupdaterects = []

    # Let's use our image that we move around the screen for example.
    dirty_rect = screen.blit(image, (x,y))
    myupdaterects.append(dirty_rect)

    dirty_rect = screen.blit(myguiapp.top_surface, myguiapp.pos)
    myupdaterects.append(dirty_rect)

    dirty_rect = screen.blit(game_panel.top_surface, game_panel.pos)
    myupdaterects.append(dirty_rect)

    # Now we update the screen!
    pygame.display.update(myupdaterects)

    # Don't forget to clear the dirty rect list!
    myupdaterects = []

    tick_count += 1
