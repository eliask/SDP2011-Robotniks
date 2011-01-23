import PCBluetooth
import time

b = PCBluetooth()

PCBluetooth.openConnection()
PCBluetooth.sendMessage(1)
time.sleep(1)
PCBluetooth.sendMessage(2)
time.sleep(1)
PCBluetooth.sendMessage(3)
time.sleep(3)
PCBluetooth.sendMessage(4)
time.sleep(3)
PCBluetooth.sendMessage(0)
time.sleep(2)
PCBluetooth.sendMessage(366)
time.sleep(1)
PCBluetooth.sendMessage(100)
time.sleep(3)
PCBluetooth.sendMessage(360-100)

