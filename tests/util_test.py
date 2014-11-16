from src.util import *

import os
from nose.tools import *

filename = "basic"

def removeFiles():
    os.remove(filename)

@with_setup(teardown = removeFiles)
def testBasicInstaParseFile():
    simpleFile = InstaParseFile(filename)
    simpleFile.write("abc")
    simpleFile.save()
    simpleFile.writeLine("def")
    simpleFile.writeLine("ghijkl")
    simpleFile.save()

    resultFile = open( filename, "r" )
    assert_equal( resultFile.readline().strip(), "abcdef" )
    assert_equal( resultFile.readline().strip(), "ghijkl" )
    resultFile.close()

@with_setup(teardown = removeFiles)
def testInstaParseFileComments():
    simpleFile = InstaParseFile(filename)
    simpleFile.writeLine("abc")
    simpleFile.comment("The above is an abc.")
    simpleFile.save()

    resultFile = open( filename, "r" )
    assert_equal( resultFile.readline().strip(), "abc" )
    assert_equal( resultFile.readline().strip(), simpleFile.commentString + " The above is an abc." )
    resultFile.close()

@with_setup(teardown = removeFiles)
def testInstaParseImport():
    simpleFile = InstaParseFile(filename)
    simpleFile.writeLine("abc")
    simpleFile.writeImportLine("import a simple library")
    simpleFile.save()

    resultFile = open( filename, "r" )
    assert_equal( resultFile.readline().strip(), "import a simple library" )
    assert_equal( resultFile.readline().strip(), "abc" )
    resultFile.close()

@with_setup(teardown = removeFiles)
def testInstaParseWrite():
    simpleFile = InstaParseFile(filename)
    simpleFile.indent()
    simpleFile.write("abc")
    simpleFile.write("def")
    simpleFile.writeLine("ghi")
    simpleFile.write("lmn")
    simpleFile.writeNewline()
    simpleFile.write("opq")
    simpleFile.save()

    resultFile = open( filename, "r" )
    assert_equal( resultFile.readline().strip(), "abcdefghi" )
    assert_equal( resultFile.readline().strip(), "lmn" )
    assert_equal( resultFile.readline().strip(), "opq" )
    resultFile.close()
