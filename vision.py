from vision.vision import *
import sys

if len(sys.argv) > 1:
    print sys.argv
    v = Vision(sys.argv[-1])
else:
    v = Vision()
v.run()
