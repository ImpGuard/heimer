""" General utility class used by the various components. """

class HeimerFile:
    """ Simple custom file class used by code generation components. """

    indentString = "    "
    commentString = "#"

    def __init__( self, name ):
        self.filename = name
        self.fileContents = ""
        self.indentLevel = 0
        self.shouldIndent = True

    def indent(self):
        self.indentLevel += 1

    def dedent(self):
        self.indentLevel -= 1

    def comment( self, line ):
        """ Writes a comment line using the commentString variable that can be adjusted. """
        self.writeLine(self.commentString + " " + line)

    def write( self, line ):
        """ Writes a line to the file, only indenting if it is supposed to.

        It will indent only if the most recent `write` call is a `writeLine` or `writeNewline` (
        ignoring other methods in this class). """
        if self.shouldIndent:
            self.fileContents += HeimerFile.indentString * self.indentLevel + line
        else:
            self.fileContents += line
        self.shouldIndent = False

    def writeLine( self, line ):
        self.write(line + "\n")
        self.shouldIndent = True

    def writeImportLine( self, line ):
        """ Helps write an import or include line at the top of the file disregarding the indent level. """
        self.fileContents = line + "\n" + self.fileContents

    def writeNewline( self ):
        """ Helper to write a simple newline, useful for adding an empty line. """
        self.fileContents += "\n"
        self.shouldIndent = True

    def save(self):
        """ Saves the HeimerFile. Ideally, use only once per HeimerFile at the end of code generation. """
        outputFile = open( self.filename, "w")
        outputFile.write(self.fileContents)
        outputFile.close()
