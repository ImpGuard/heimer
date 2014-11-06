from fixtures import *
from nose.tools import *

tests = [
    getTest(0, "graph", ".cpp", 1)
]

def testCPPGen():
    fixture = CPPFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
