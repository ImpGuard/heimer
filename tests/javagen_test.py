from fixtures import *
from nose.tools import *

tests = [
    getTest(0, "graph", ".java", 1)
]

def testJavaGen():
    fixture = JavaFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
