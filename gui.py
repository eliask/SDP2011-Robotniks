#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This creates the interface to switch between strategies.
"""

from common.world import *
from communication.robot_interface2 import *
from gooeypy.const import *
from strategy.strategies import *
from strategy.strategies import strategies
from vision2.vision import *
import pygame, gooeypy
import os, sys
import logging
#logging.basicConfig(level=logging.DEBUG)

strategy_dir = os.path.abspath('.') + '/strategy'

world = World()
v = Vision(world)

_colour = 'yellow'
if len(sys.argv) > 1:
  _colour = sys.argv[1]

ai_name = 'null'
if len(sys.argv) > 2:
  ai_name = sys.argv[2]

ai = strategies[ai_name]( world, RealRobotInterface() )
ai.setColour(_colour)

def change_strategy(strategy):
  global ai
  ai = strategies[strategy]( world, RealRobotInterface() )
  ai.setColour(_colour)
  print 'Changed strategy to:', strategy

goal = 'left'
def change_goal(new_goal):
  if goal != new_goal:
    world.swapGoals()
  print 'Changed goal to:', goal

def change_colour(colour):
  global _colour
  _colour = colour
  #ai.setColour(colour)
  print 'Changed colour to', colour

# Setup the GUI components:
pygame.init()
clock = pygame.time.Clock()
height = 21 * len(strategies)
screen = pygame.display.set_mode((640, height), pygame.SRCALPHA)
gui = gooeypy.Container(width=640, height=height, surface=screen)

hbox = gooeypy.HBox(x=0, y=0)
gui.add(hbox)

strategy_select = gooeypy.SelectBox(width=200, scrollable=True)
for strategy in strategies:
  strategy_select.add(strategy, strategy)
hbox.add(strategy_select)

left_goal_button = gooeypy.Button('Blue->Left')
left_goal_button.click = lambda: change_goal('left')
hbox.add(left_goal_button)

right_goal_button = gooeypy.Button('Blue->Right')
right_goal_button.click = lambda: change_goal('right')
hbox.add(right_goal_button)

blue_button = gooeypy.Button('Blue')
blue_button.click = lambda: change_colour('blue')
hbox.add(blue_button)

yellow_button = gooeypy.Button('Yellow')
yellow_button.click = lambda: change_colour('yellow')
hbox.add(yellow_button)

quit = False
selected_strategy = None

while not quit:
  # The main loop

  v.processFrame()
  ai.run()
  ai.sendMessage()

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
