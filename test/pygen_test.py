from fixtures import *
from nose.tools import *

import sys

tests = [
    getTest(True, "image", "py")
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
