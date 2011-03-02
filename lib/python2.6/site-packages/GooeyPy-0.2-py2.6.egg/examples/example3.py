"""
This example shows a cool way of handling a main menu system, which tends to
be a rather common thing that most games do.
"""
import sys
sys.path.insert(0, "..")

import pygame
import gooeypy as gui
from gooeypy.const import *

pygame.init()

# Ok, this is really really cool... a CLOCK!!! Ok, so maybe that's not so new...
clock = pygame.time.Clock()

screen = pygame.display.set_mode((640, 480), pygame.SRCALPHA)

app = gui.Container(width=640, height=480, surface=screen)


class Menus(gui.Container):
    """ We have this to hold all of our menus. Keeps things clean and tidy. """

    def activate(self, index):
        """ Basically what we do here is deactivate all the widgets (menus) and
            then activate the menu at index. When a widget is not active, it
            simply disappears. """
        for w in self.widgets:
            w.active = False
        self.widgets[index].active = True


menus = Menus(width=640, height=480)
# There is one **very important** thing I want to note here. If you ever get
# frustrated that things in your container (remember, Menus is just a sub class
# of gui.Container) don't work, it's probably because they aren't getting events
# passed to them. Be sure to make the container spread the whole area that your
# widgets are! Widgets that are placed out of the bounds of your container
# simply won't work! That's why we are setting the width and height here.

app.add(menus)


# Let's create a generic button that will bring us to the main menu.
back_button = gui.Button("main menu", x=20, y=-20, valign="bottom")
back_button.connect(CLICK, menus.activate, 0)


# Now let's create our menus.
mainmenu = gui.Container(width=640, height=480)
b1 = gui.Button("menu1")
b1.connect(CLICK, menus.activate, 1)
b2 = gui.Button("menu2")
b2.connect(CLICK, menus.activate, 2)
menubar = gui.HBox(align="center", valign="bottom", y=-20, spacing=20)
menubar.add(b1, b2)
data = "This example shows a cool way of handling a main menu system, which tends to be a rather common thing that most games do."
tb = gui.TextBlock(value=data, align="center", y=20, width=400)
mainmenu.add(menubar, tb)

menu1 = gui.Container(width=640, height=480)
w1 = gui.Input(align="center", valign="center")
menu1.add(back_button, w1)

menu2 = gui.Container(width=640, height=480)
w2 = gui.Button("I do nada!", align="center", valign="center")
menu2.add(back_button, w2)

# Now we add our menus to... menus!
menus.add(mainmenu, menu1, menu2)

# And active the mainmenu.
menus.activate(0)


# Let's run our app and see if it works!
quit = False
while not quit:
    clock.tick(20)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            quit = True

        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()


    app.run(events)
    app.draw()

    pygame.display.flip()

# Now, was that very hard? Look how little code it took to get a menu system
# setup! This is a big goal for GooeyPy, to be able to get what it needs to get
# done with as little code as possible.
