"""
This script syntax checks all python files in the repository and runs all
defined tests.
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
Directories to ignore when scanning for py files.
"""
IGNORE_DIRS = ['lib']

"""
The directory tests are stored in.
"""
TEST_DIR = BASE_DIR + os.sep + "test"

"""
Checks the syntax of all the python files.
"""
def check_syntax(error_file):
	errors = 0
	
	for f in find_py(BASE_DIR):
		try:
			py_compile.compile(f, None, f.replace(BASE_DIR + os.sep, ""), True)
			os.remove(f + "c")
		except py_compile.PyCompileError:
			errors += 1
			exc_value = sys.exc_info()[1]
			error_file.write(exc_value.__str__().rstrip() + "\n")
	
	if errors:
		print("Encountered " + errors.__str__() + " syntax error(s).  " \
			+ "Details in %s", ERROR_FILE)
	else:
		print("No syntax errors.")

"""
Find all .py files below the base (git) directory.
"""
def find_py(d):
	files = []
	
	for f in os.listdir(d):
		path = os.path.join(d, f)
		
		if os.path.isdir(path) and not f in IGNORE_DIRS:
			files += find_py(path)
		elif(re.match(".*\.py$", f)):
			files.append(path)
	
	return files

"""
Runs all the tests.
"""
def run_tests(error_file):
	if __name__ == "__main__":
		tld = TEST_DIR
	else:
		tld = BASE_DIR
	
	suite = unittest.TestLoader().discover(TEST_DIR, top_level_dir = tld)
	result = unittest.TextTestRunner(stream = error_file).run(suite)
	
	if(result.wasSuccessful()):
		error_file.truncate(0)
		print("All tests passed.")
	else:
		print("%d test(s) failed.  Details in %s" % \
			(len(result.errors) + len(result.failures), ERROR_FILE))

"""
Finds test files.
"""
def find_tests():
	tests = []
	
	for f in find_py(TEST_DIR):
		if "__init__.py" in f: continue
		
		t = f.replace(TEST_DIR + os.sep, "")\
		     .replace(".py", "")\
		     .replace(os.sep, ".")
		if "." in t: tests.append(t)
	
	return tests

"""
Le's do dis!
"""
def test():
	error_file = open(ERROR_FILE, "w")
	
	check_syntax(error_file)
	run_tests(error_file)
	
	error_file.close()
	
	if(os.path.getsize(ERROR_FILE) > 0):
		sys.exit(1)
	else:
		os.remove(ERROR_FILE)

if __name__ == "__main__":
	test()
