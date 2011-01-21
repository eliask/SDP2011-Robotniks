import sys, traceback, Ice
import Robotnik

def sendMessage(message):
	status = 0
	ic = None
	try:
		ic = Ice.initialize(sys.argv)
		base = ic.stringToProxy("SimpleCommander:default -p 10000")
		commander = Robotnik.CommanderPrx.checkedCast(base)
		if not commander:
			raise RuntimeError("Invalid proxy")
		commander.sendMessage(1)
	except:
		traceback.print_exc()
		status = 1
	
	if ic:
		try:
			ic.destroy()
		except:
			traceback.print_exc()
			status = 1

	print(status)

sendMessage(1)
