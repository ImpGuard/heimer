from fixtures import *
from nose.tools import *

tests = [
    getTestByName(0, "image", "java"),
    getTest(0, "vector.format", "vector.java", "vector_pass1.input", "vector_pass1.sln"),
    getTest(0, "vector.format", "vector.java", "vector_pass2.input", "vector_pass2.sln"),
    getTest(0, "vector.format", "vector.java", "vector_pass3.input", "vector_pass3.sln"),
    getTest(0, "vector.format", "vector.java", "vector_pass4.input", "vector_pass4.sln"),
    getTest(4, "vector.format", "vector.java", "vector_fail1.input", "vector_fail1.sln"),
    getTest(4, "vector.format", "vector.java", "vector_fail2.input", "vector_fail2.sln")
]

def testJavaGen():
    fixture = JavaFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
