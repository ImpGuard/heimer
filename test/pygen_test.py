from fixtures import *
from nose.tools import *

import sys, os

tests = [
    getTestByName(0, "image", "py"),
    getTest(0, "Vector.format", "Vector.py", "Vector_pass1.input", "Vector_pass1.sln"),
    getTest(0, "Vector.format", "Vector.py", "Vector_pass2.input", "Vector_pass2.sln"),
    getTest(0, "Vector.format", "Vector.py", "Vector_pass3.input", "Vector_pass3.sln"),
    getTest(0, "Vector.format", "Vector.py", "Vector_pass4.input", "Vector_pass4.sln"),
    getTest(4, "Vector.format", "Vector.py", "Vector_fail1.input", "Vector_fail1.sln"),
    getTest(4, "Vector.format", "Vector.py", "Vector_fail2.input", "Vector_fail2.sln")
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
