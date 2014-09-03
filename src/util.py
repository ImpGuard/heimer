""" General utility class used by the various components. """

class HeimerFile:
    """ Simple custom file class used by code generation components. """

    indentString = "    "
    commentString = "#"

    def __init__( self, name ):
        self.filename = name
        self.fileContents = ""
        self.indentLevel = 0

    def indent(self):
        self.indentLevel += 1

    def dedent(self):
        self.indentLevel -= 1

    def comment( self, line ):
        """ Writes a comment line using the commentString variable that can be adjusted. """
        self.writeLine(self.commentString + " " + line)

    def write( self, line ):
        self.fileContents += HeimerFile.indentString * self.indentLevel + line

    def writeLine( self, line ):
        self.write(line + "\n")

    def writeImportLine( self, line ):
        """ Helps write an import or include line at the top of the file disregarding the indent level. """
        self.fileContents = line + "\n" + self.fileContents

    def save(self):
        """ Saves the HeimerFile. Ideally, use only once per HeimerFile at the end of code generation. """
        outputFile = open( self.filename, "w")
        outputFile.write(self.fileContents)
        outputFile.close()
