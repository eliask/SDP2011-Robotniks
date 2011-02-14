"""
This script runs all defined tests.
"""

import os, sys, unittest2 as unittest

"""
The base directory (git root directory).
"""
BASE_DIR = os.getcwd()

"""
The directory tests are stored in.
"""
TEST_DIR = BASE_DIR + os.sep + "test"

"""
Runs all the tests.
"""
def run_tests():
	suite = unittest.TestLoader().discover(TEST_DIR, top_level_dir = BASE_DIR)
	result = unittest.TextTestRunner(verbosity=2).run(suite)

	if not result.wasSuccessful():
		sys.exit(1)

if __name__ == "__main__":
	run_tests()
