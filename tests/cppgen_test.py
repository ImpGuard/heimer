from testSuite import getTests
from fixtures import checkTest

from fixtures import CPPFixture

def testCPPGen():
    fixture = CPPFixture(getTests(".cpp"))
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
