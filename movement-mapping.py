from communication.robot_interface2 import RealRobotInterface
import time

IF = RealRobotInterface()

#time.sleep(3)

DT = 1/25.0
for t in range(3/DT):
    IF.sendMessage()
    time.sleep(DT)

settings = range(-3,4)
motors = (IF.drive1, IF.drive2, IF.turn1, IF.turn2)

print "Starting movement mapping:"
print "(vision/World /should/ be logging everything)"
print

print "Turn wheels independently while doing nothing else"
for i in settings:
    IF.turn1(i); IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

for i in settings:
    IF.turn2(i); IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "Turn wheels at the same time the same way, in both ways"
for i in settings:
    IF.turn1(i)
    IF.turn2(i); IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "Turn the wheels to different directions at the same time"
for i in settings:
    IF.turn1(i)
    IF.turn2(-i); IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "Reset and move back and forth"
IF.reset()
IF.sendMessage()
time.sleep(1)

for i in settings:
    IF.drive1(i)
    IF.drive2(i); IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "Drive using just one wheel at a time"
for i in settings:
    IF.drive1(i)
    IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

for i in settings:
    IF.drive2(i)
    IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "\"Drive in two directions at once\""
for i in settings:
    IF.drive1(i)
    IF.drive2(-i)
    IF.sendMessage()
    time.sleep(1)
IF.sendMessage()
time.sleep(1)

print "Drive with both while systematically testing each static turning angle"


print "Drive with both while trying out different and constant turning speeds"


print "Kick and possibly do stuff while kicking randomly, etc."


print "Try random combinations of all commands"

time.sleep(2)
while True:
    if random.random() < 0.25:
        IF.drive1( random.randint(-3,3) )
    if random.random() < 0.25:
        IF.drive2( random.randint(-3,3) )
    if random.random() < 0.25:
        IF.turn1( random.randint(-3,3) )
    if random.random() < 0.25:
        IF.turn2( random.randint(-3,3) )
    if random.random() < 0.2:
        IF.kick()
    if random.random() < 0.05:
        IF.reset()

    for r in random.randint(1,11):
        IF.sendMessage()
        time.sleep(DT)
