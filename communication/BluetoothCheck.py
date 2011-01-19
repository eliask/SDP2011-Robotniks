# nxt-python library
import nxt.bluesock

# connect and read device info
socket = nxt.bluesock.BlueSock("00:16:53:07:D6:2B")
brick = socket.connect()
brick.get_device_info()
