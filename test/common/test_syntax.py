import os, py_compile, re, test.test as test, unittest2 as unittest

"""
Directories to ignore when scanning for py files.
"""
IGNORE_DIRS = ['lib']

"""
This unit test tests all python files have valid syntax.
"""
class TestSyntax(unittest.TestCase):
	
	"""
	Checks the syntax of all the python files.
	"""
	def test_syntax(self):
		for f in self.find_py(test.BASE_DIR):
			py_compile.compile(f, None, f.replace(test.BASE_DIR + os.sep, ""), True)
			os.remove(f + "c")
	
	"""
	Find all .py files below the base (git) directory.
	"""
	def find_py(self, d):
		files = []
		
		for f in os.listdir(d):
			path = os.path.join(d, f)
			
			if os.path.isdir(path) and not f in IGNORE_DIRS:
				files += self.find_py(path)
			elif(re.match(".*\.py$", f)):
				files.append(path)
		
		return files
