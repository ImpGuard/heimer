from testSuite import getTests
from fixtures import checkTest

from fixtures import PythonFixture

def testPyGen():
    fixture = PythonFixture(getTests(".py"))
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
