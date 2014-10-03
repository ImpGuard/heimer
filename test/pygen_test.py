from fixtures import *
from nose.tools import *

import sys, os

tests = [
    getTest(True, "image", "py"),
    (True, os.path.join("test/tests/pass/", "Vector.format"), os.path.join("test/tests/pass/", "Vector_pass1.py"), os.path.join("test/tests/pass/", "Vector_pass1.input"), os.path.join("test/tests/pass/", "Vector_pass1.sln"))
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
