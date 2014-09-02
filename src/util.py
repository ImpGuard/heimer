""" General utility class used by the various components. """

class HeimerFile:
    """ Simple custom file class used by code generation components. """

    indentString = "    "

    def __init__ ( self, name ):
        self.internalFile = open ( name, "w" )
        self.indentLevel = 0

    def indent():
        self.indentLevel += 1

    def dedent():
        self.indentLevel -= 1

    def write (line):
        self.internalFile.write (HeimerFile.indentString * self.indentLevel + line)

    def writeLine (line):
        self.write (line + "\n")

    def close():
        self.internalFile.close()


