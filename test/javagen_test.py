from fixtures import *

tests = [
    getTest(True, "image", "java")
]

def testJavaGen():
    fixture = JavaFixture(tests)
    fixture.runAllTests()
