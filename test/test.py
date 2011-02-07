"""
This script runs all defined tests.
"""

import os, py_compile, re, sys, unittest2 as unittest

"""
The base directory (git root directory).
"""
BASE_DIR = os.getcwd()

"""
The file to store the error log in.
"""
ERROR_FILE = "test/error.log"

"""
The directory tests are stored in.
"""
TEST_DIR = BASE_DIR + os.sep + "test"

"""
Runs all the tests.
"""
def run_tests():
	error_file = open(ERROR_FILE, "w")
	
	suite = unittest.TestLoader().discover(TEST_DIR, top_level_dir = BASE_DIR)
	result = unittest.TextTestRunner(stream = error_file).run(suite)
	
	error_file.close()
	
	if(result.wasSuccessful()):
		os.remove(ERROR_FILE)
		print("All tests passed.")
	else:
		print("%d test(s) failed.  Details in %s" % \
			(len(result.errors) + len(result.failures), ERROR_FILE))
		sys.exit(1)

if __name__ == "__main__":
	run_tests()
