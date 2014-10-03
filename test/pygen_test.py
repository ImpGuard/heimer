from fixtures import *
from nose.tools import *

import sys, os

tests = [
    getTest(True, "image", "py"),
    (True, os.path.join("test/tests/pass/", "Vector.format"), os.path.join("test/tests/pass/", "Vector_pass.py"), os.path.join("test/tests/pass/", "Vector_pass1.input"), os.path.join("test/tests/pass/", "Vector_pass1.sln")),
    (True, os.path.join("test/tests/pass/", "Vector.format"), os.path.join("test/tests/pass/", "Vector_pass.py"), os.path.join("test/tests/pass/", "Vector_pass2.input"), os.path.join("test/tests/pass/", "Vector_pass2.sln")),
    (True, os.path.join("test/tests/pass/", "Vector.format"), os.path.join("test/tests/pass/", "Vector_pass.py"), os.path.join("test/tests/pass/", "Vector_pass3.input"), os.path.join("test/tests/pass/", "Vector_pass3.sln")),
    (True, os.path.join("test/tests/pass/", "Vector.format"), os.path.join("test/tests/pass/", "Vector_pass.py"), os.path.join("test/tests/pass/", "Vector_pass4.input"), os.path.join("test/tests/pass/", "Vector_pass4.sln"))
]

def testPyGen():
    fixture = PythonFixture(tests)
    testGenerator = fixture.generateTests()
    for test in testGenerator:
        yield checkTest, test
