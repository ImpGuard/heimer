from testSuite import getTests
from fixtures import checkTest

from fixtures import JavaFixture

def testJavaGen():
    fixture = JavaFixture(getTests(".java"))
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
