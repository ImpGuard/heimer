from fixtures import *
from nose.tools import *

import sys, os

tests = [
    getTestByName(0, "image", "py"),
    getTest(0, "vector.format", "vector.py", "vector_pass1.input", "vector_pass1.sln"),
    getTest(0, "vector.format", "vector.py", "vector_pass2.input", "vector_pass2.sln"),
    getTest(0, "vector.format", "vector.py", "vector_pass3.input", "vector_pass3.sln"),
    getTest(0, "vector.format", "vector.py", "vector_pass4.input", "vector_pass4.sln"),
    getTest(4, "vector.format", "vector.py", "vector_fail1.input"),
    getTest(4, "vector.format", "vector.py", "vector_fail2.input")
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
