"""
This creates the interface to switch between strategies.
"""
import gooeypy
from gooeypy.const import *
import os
import pygame
import sys
from strategy.strategies import strategies

"""
Points to the strategy dir
"""
strategy_dir = os.path.abspath('.') + '/strategy'

"""
The method to change the strategy.
"""
def change_strategy(strategy):
  print 'Changed strategy to:', strategy

"""
The method to change the goal.
"""
def change_goal(goal):
  print 'Changed goal to:', goal

"""
The method to change the colour.
"""
def change_colour(colour):
  print 'Changed colour to', colour

"""
Setup the GUI components.
"""
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((640, 135), pygame.SRCALPHA)
gui = gooeypy.Container(width=640, height=135, surface=screen)

hbox = gooeypy.HBox(x=0, y=0)
gui.add(hbox)

strategy_select = gooeypy.SelectBox(width=200, scrollable=True)
for strategy in strategies:
  strategy_select.add(strategy, strategy)
hbox.add(strategy_select)

left_goal_button = gooeypy.Button('Left Goal')
left_goal_button.click = lambda: change_goal('left')
hbox.add(left_goal_button)

right_goal_button = gooeypy.Button('Right Goal')
right_goal_button.click = lambda: change_goal('right')
hbox.add(right_goal_button)

blue_button = gooeypy.Button('Blue')
blue_button.click = lambda: change_colour('blue')
hbox.add(blue_button)

yellow_button = gooeypy.Button('Yellow')
yellow_button.click = lambda: change_colour('yellow')
hbox.add(yellow_button)

"""
The GUI loop.
"""
quit = False
selected_strategy = None
while not quit:
  clock.tick(30)

  # You'd think there'd be a 'connectable' event for the selection
  # changing, but unfortunately not.
  if len(strategy_select.values) != 0:
    new_strategy = strategy_select.values.pop()
    if new_strategy != selected_strategy:
      selected_strategy = new_strategy
      change_strategy(selected_strategy)

  gui.run(pygame.event.get())
  gui.draw()

  pygame.display.flip()
