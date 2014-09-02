from util import *

import os
from nose.tools import *

filename1 = "basic"
filename2 = "advanced"

def removeFiles():
    try:
        os.remove(filename1)
        os.remove(filename2)
    except:
        pass

@with_setup(teardown = removeFiles)
def testBasicHeimerFile():
    simpleFile = HeimerFile(filename1)
    simpleFile.write("abc")
    simpleFile.save()
    simpleFile.writeLine("def")
    simpleFile.writeLine("ghijkl")
    simpleFile.save()

    resultFile = open(filename1, "r")
    assert_equal( resultFile.readline().strip(), "abcdef" )
    assert_equal( resultFile.readline().strip(), "ghijkl" )
    resultFile.close()

@with_setup(teardown = removeFiles)
def testVirtualMachine():
    VM = VirtualMachine()
    VM.openFile(filename1)
    VM.writeLine("def func():")
    VM.indent()
    VM.openFile(filename2)
    VM.writeLine("def func2():")
    VM.indent()
    VM.writeLine("print 'hi'")
    VM.dedent()
    VM.switchTo(filename1)
    VM.writeLine("pass")
    VM.dedent()
    VM.save()

    resultFile = open(filename1, "r")
    assert_equal( resultFile.readline().strip(), "def func():" )
    assert_equal( resultFile.readline().rstrip(), "    pass" )
    resultFile.close()

    resultFile = open(filename2, "r")
    assert_equal( resultFile.readline().strip(), "def func2():")
    assert_equal( resultFile.readline().rstrip(), "    print 'hi'")
    resultFile.close()


