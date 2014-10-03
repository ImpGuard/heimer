from fixtures import *
from nose.tools import *

import sys

tests = [
    getTest(True, "image", "java")
]

def testJavaGen():
    fixture = JavaFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test

@with_setup(setupTest, teardownTest)
def checkTest(test):
    opcode, val = test()
    if opcode == 1:
        assert False, "Output does not match solution\n\n" + val
    elif opcode == 2:
        assert False, "Format File Error\n\n" + val
    elif opcode == 3:
        assert False, "Compilation Error\n\n" + val
    elif opcode == 4:
        assert False, "Runtime Error\n\n" + val
