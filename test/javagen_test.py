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
