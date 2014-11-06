from fixtures import *
from nose.tools import *

import sys, os

tests = [
    getTest(0, "graph", ".py", 1)
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
