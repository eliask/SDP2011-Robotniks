"""
This example is to demonstrate GooeyPy's widgets and functionality.
"""

import sys
sys.path.insert(0, "..")

import gooeypy as gui
import pygame
from gooeypy.const import *

pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 480), pygame.SRCALPHA)

# Since version 0.2 any widget behaves as a top level element. But all top-level
# widgets must be passed a pygame Surface (which screen is) that it will draw to.
myguiapp = gui.Container(width=640, height=480, surface=screen)

# Create some widgets (if any of this is confusing, just read the docs for the
# widget).
w1 = gui.Button("reset", x=20, y=30)
w2 = gui.Input(x=100, y=30, width=240)
w3 = gui.Switch(x=500, y=30)
w4 = gui.HSlider(min_value=20, length=10, x=200, y=160)
w9 = gui.VSlider(length=40, x=600, y=160, step=False)
l1 = gui.Label(value="Pulsate:", x=395, y=30, font_size=25)

data = """This example is to demonstrate GooeyPy's widgets and functionality.

You can also have line breaks."""
tb = gui.TextBlock(value=data, x=200, y=350, width=300)

# Add our widgets to our App.
myguiapp.add(w1,w2,w3,w4,w9,l1,tb)

# Now lets make us a VBox, which will automatically position widgets inside of it
# vertically. Give it an ugly bgcolor too for fun.
b1 = gui.VBox(x=20, y=200, bgcolor="(20,200,0)", padding=5, spacing=5)

w5 = gui.Button("Value 1")
w6 = gui.Button("Value 2")
w7 = gui.Button("Value 3")
w8 = gui.Button("Value 4")

b1.add(w5,w6,w7,w8)

# And add it to our App.
myguiapp.add(b1)


# Lets create a SelectBox. First I want to make a switch for selecting
# wether or not the select box should allow multiple selections.
mon = gui.Switch(False, labels=("Multiple","Single"), options=(True, False),
        x=430, y=200, min_width=110)
myguiapp.add(mon)
# Ah heck, lets have another switch.
don = gui.Switch(False, labels=("Disabled", "Enabled"), options=(True, False),
        x=430, y=260, min_width=110)
myguiapp.add(don)

# Now we make the SelectBox. Notice how we link the value of our switch to the
# multiple and disabled values here. We could accomplish the same thing by using
# widget.connect, this is just easier and way cooler.
sb1 = gui.SelectBox(disabled=don.link("value"), multiple=mon.link("value"),
        x=200, y=200, width=200, scrollable=False, height=100)
sb1.add("Value 1", "value1")
sb1.add("Value 2", "value2")
sb1.add("Value 3", "value3")

# Here we are doing something a little bit different, we are setting the value
# to be a widget (w4 is a Slider btw). Normally you have to use
# widget.link("value"), but for a SelectBox, we can give it a widget directly.
sb1.add(w4, "slidervalue")

# Lets do it again, except this time with the input widget.
sb1.add(w2, "inputvalue")

# Ok, now we add it to the App...
myguiapp.add(sb1)



# Connections are still useful, lets make one. Here is our callback.
def callback():
    # Basically, if w3 (which is a switch) is on, we make w2 (an input widget)
    # pulsate. If it's off, we make it like not pulsate.
    if w3.value == True:
        for s in w2.stylesets.values():
            s["effect"] = "pulsate 5"
    else:
        for s in w2.stylesets.values():
            s["effect"] = "none"

# Now we connect our switch to our call back with the event CHANGE (which is
# fired when ever the widget changes).
w3.connect(CHANGE, callback)


# Lets make another connection just for fun.
def callback():
    w2.value = "GooeyPy is cool!"
w1.connect(CLICK, callback)


# Now lets run our app!
quit = False
while not quit:
    clock.tick(30)

    events = pygame.event.get()

    for event in events:
        if event.type == QUIT:
            quit = True
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                sys.exit()

    myguiapp.run(events)
    myguiapp.draw()

    pygame.display.flip()

# Ok, that's all! You can read the docs for more information about the widgets,
# styling and the like.
