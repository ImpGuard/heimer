""" General utility class used by the various components. """

class HeimerFile:
    """ Simple custom file class used by code generation components. """

    indentString = "    "

    def __init__( self, name ):
        self.filename = name
        self.fileContents = ""
        self.indentLevel = 0

    def indent(self):
        self.indentLevel += 1

    def dedent(self):
        self.indentLevel -= 1

    def write( self, line ):
        self.fileContents += HeimerFile.indentString * self.indentLevel + line

    def writeLine( self, line ):
        self.write(line + "\n")

    def save(self):
        outputFile = open( self.filename, "a")
        outputFile.write(self.fileContents)
        self.fileContents = ""
        outputFile.close()

class VirtualMachine:
    """ Helper class for code generation to abstract out file editing logic. """

    def __init__(self):
        self.files = dict()
        self.currentFile = None

    def openFile( self, filename ):
        self.files[filename] = HeimerFile(filename)
        self.currentFile = self.files[filename]

    def switchTo( self, filename ):
        self.currentFile = self.files[filename]

    def write( self, line ):
        self.currentFile.write(line)

    def writeLine( self, line ):
        self.currentFile.writeLine(line)

    def indent(self):
        self.currentFile.indent()

    def dedent(self):
        self.currentFile.dedent()

    def save(self):
        for filename in self.files:
            self.files[filename].save()


