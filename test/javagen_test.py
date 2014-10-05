from fixtures import *
from nose.tools import *

tests = [
    getTestByName(0, "image", "java")
]

def testJavaGen():
    fixture = JavaFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
