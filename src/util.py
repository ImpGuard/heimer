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

    def writeNewline(self):
        """ Helper to write a simple newline, useful for adding an empty line. """
        self.fileContents += "\n"
        self.shouldIndent = True

    def save(self):
        """ Saves the HeimerFile. Ideally, use only once per HeimerFile at the end of code generation. """
        outputFile = open( self.filename, "w")
        outputFile.write(self.fileContents)
        outputFile.close()

    def setExtension( self, extensionString ):
        """ Sets the extension of this file to the given extension, if applicable. """
        extensionIndex = self.filename.rfind("." + extensionString)
        if extensionIndex == -1 or extensionIndex != len(self.filename) - len(extensionString) - 1:
            self.filename += "." + extensionString

class StringConstants:

    HEAD_TAG = "<head>"
    OPTIONS_TAG = "<options>"
    OBJECTS_TAG = "<objects>"
    BODY_TAG = "<body>"
    INLINE_COMMENT = "#"
    DEFAULT_SINGLE_LINE_DELIMITER = " "
    INTEGER_TYPE = "int"
    FLOAT_TYPE = "float"
    STRING_TYPE = "string"
    BOOL_TYPE = "bool"
    LIST_TYPE = "list"
    LINE_ONE_OR_MORE = "+"
    LINE_ZERO_OR_MORE = "*"
    SEPARATE_BY_ADDITIONAL_NEWLINE_MODE = "!"

def isPrimitive(typeName):
    return typeName == StringConstants.INTEGER_TYPE or typeName == StringConstants.FLOAT_TYPE or \
        typeName == StringConstants.BOOL_TYPE or typeName == StringConstants.STRING_TYPE or \
        isList(typeName)

def isInteger(typeName):
    return typeName == StringConstants.INTEGER_TYPE

def isFloat(typeName):
    return typeName == StringConstants.FLOAT_TYPE

def isString(typeName):
    return typeName == StringConstants.STRING_TYPE

def isBool(typeName):
    return typeName == StringConstants.BOOL_TYPE

def isList(typeName):
    """ List is of the form 'list(listType)' where listType is a non-list primitive. """
    if len(typeName) <= 4:
        return False
    if typeName.find(StringConstants.LIST_TYPE) == 0 and \
        typeName[len(StringConstants.LIST_TYPE)] == "(" and \
        typeName[-1] == ")":
        listType = typeName[ len(StringConstants.LIST_TYPE) + 1 : len(typeName) - 1 ].strip()
        if isPrimitive(listType) and not isList(listType):
            return True
        else:
            return False
    return False

def listType(typeName):
    if isList(typeName):
        return typeName[ len(StringConstants.LIST_TYPE) + 1 : len(typeName) - 1 ].strip()
    else:
        return None
