from testSuite import getParserTests
from fixtures import checkTest

from fixtures import PythonFixture

def testPyGen():
    fixture = PythonFixture(getParserTests(".py"))
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
