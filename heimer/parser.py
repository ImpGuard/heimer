class StringConstants:

    HEAD_TAG = "<head>"
    OPTIONS_TAG = "<options>"
    SINGLE_TAG = "<single>"
    MULTIPLE_TAG = "<multiple>"
    BODY_TAG = "<body>"
    INLINE_COMMENT = "#"
    DEFAULT_SINGLE_LINE_DELIMITER = " "
    INTEGER_TYPE = "int"
    FLOAT_TYPE = "float"
    STRING_TYPE = "string"
    BOOL_TYPE = "bool"
    LIST_TYPE = "list"
    SEPARATE_BY_ADDITIONAL_NEWLINE_MODE = "!"

def lineStartsValidTag(line):
    return line == StringConstants.HEAD_TAG or \
        line == StringConstants.OPTIONS_TAG or \
        line == StringConstants.SINGLE_TAG or \
        line == StringConstants.MULTIPLE_TAG or \
        line == StringConstants.BODY_TAG

def stripCommentsAndWhitespaceFromLine(line):
    # FIXME: Allow using "#" as a separator in <head> tag.
    firstInlineCommentIndex = line.find(StringConstants.INLINE_COMMENT)
    if firstInlineCommentIndex == -1:
        return line
    return line[:firstInlineCommentIndex].strip()

class CommandLineOption:

    def __init__( self, flagName, variableName, typeName ):
        self.flagName = flagName
        self.variableName = variableName
        self.typeName = typeName

class Type:

    def __init__( self, rawName ):
        # Remove whitespace from the raw name.
        # FIXME: Do not allow types such as "s tri ng" to be parsed.
        self.name = rawName.split(r"\s").join("")

    def isInteger():
        return self.name == StringConstants.INTEGER_TYPE

    def isFloat():
        return self.name == StringConstants.FLOAT_TYPE

    def isString():
        return self.name == StringConstants.STRING_TYPE

    def isBool():
        return self.name == StringConstants.BOOL_TYPE

    def isList():
        return self.name.find(StringConstants.LIST_TYPE) == 0 and \
            self.name[len(StringConstants.LIST_TYPE)] == "(" and \
            self.name[-1] == ")"

    def listType():
        return Type(self.name[ len(StringConstants.LIST_TYPE) : len(self.name) - 1 ]) if self.isList() else None

class Variable:

    def __init__( self, name, inputType ):
        self.name = name
        self.inputType = inputType
        self.instanceRepititionModeString = ""
        self.shouldSeparateInstancesByAdditionalNewline = False
        self.requiresNewlineAfterLastInstance = False

    def setInstanceRepititionModeFromString( self, instanceRepititionModeString ):
        self.shouldSeparateInstancesByAdditionalNewline = instanceRepititionModeString[-1] == SEPARATE_BY_ADDITIONAL_NEWLINE_MODE
        if self.shouldSeparateInstancesByAdditionalNewline:
            instanceRepititionModeString = instanceRepititionModeString[:-1]
        self.instanceRepititionModeString = instanceRepititionModeString

class UserDefinedInputClass:

    def __init__( self, name, maySpanMultipleLines ):
        self.name = name
        self.fields = []
        self.maySpanMultipleLines = maySpanMultipleLines

    def addFieldFromVariable( self, variable ):
        self.fields.append(variable)

class HeadTag:

    def __init__(self):
        self.delimiterString = StringConstants.DEFAULT_SINGLE_LINE_DELIMITER

    def setDelimiter( self, delimiterString ):
        self.delimiterString = delimiterString

class OptionsTag:

    def __init__(self):
        self.options = []

    def addCommandLineOption( flagName, variableName, typeName ):
        self.options.append(CommandLineOption( flagName, variableName, typeName ))

class SingleTag:

    def __init__( self, lineDelimiter ):
        self.classes = []
        self.lineDelimiter = lineDelimiter

    def addUserDefinedInputClass(className):
        self.classes.append(className)

class MultipleTag:

    def __init__(self):
        self.classes = []

    def addUserDefinedInputClass(className):
        self.classes.append(className)

class BodyTag:

    def __init__(self):
        self.globalVariables = []

    def addGlobalVariable( self, globalVariable ):
        self.globalVariables.append(globalVariable)

class HeimerInputParser:

    def __init__( self, heimerInputFileName ):
        self.tagLineMarkerIntervals = {}
        self.parseFailureMessage = ""
        self.parsingFailed = False
        try:
            heimerFile = open( heimerInputFileName, "r" )
            self.heimerInputAsLines = heimerFile.read().split("\n")
            heimerFile.close()
        except IOError:
            failParsingWithMessage("Could not find file " + heimerInputFileName + ".")
            self.heimerInputAsLines = []
        self.computeTagIntervals()
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            failParsingWithMessage("Input file requires a body tag.")

    def failParsingWithMessage(message):
        if not parsingFailed:
            self.parsingFailed = True
            self.parseFailureMessage = message

    def nextTagLocationFromLineMarker( self, marker ):
        while marker < len(self.heimerInputAsLines):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.heimerInputAsLines[marker])
            if lineStartsValidTag(currentStrippedLine):
                return marker
            marker += 1
        return len(self.heimerInputAsLines)

    def firstLineMarkerWithText(self):
        marker = 0
        for line in self.heimerInputAsLines:
            if stripCommentsAndWhitespaceFromLine(line):
                return marker
            marker += 1
        return -1

    def computeTagIntervals(self):
        lineMarkerBegin = self.firstLineMarkerWithText()
        if lineMarkerBegin >= len(self.heimerInputAsLines):
            return failParsingWithMessage("Input file empty or commented out.")
        if not lineStartsValidTag(self.heimerInputAsLines[lineMarkerBegin]):
            return failParsingWithMessage("Expected tag at line " + str(lineMarkerBegin) + ".")
        while lineMarkerBegin < len(self.heimerInputAsLines):
            if self.heimerInputAsLines[lineMarkerBegin] in self.tagLineMarkerIntervals:
                return failParsingWithMessage("Duplicate tag name at line " + str(lineMarkerBegin) + ".")
            lineMarkerEnd = self.nextTagLocationFromLineMarker(lineMarkerBegin + 1)
            self.tagLineMarkerIntervals[self.heimerInputAsLines[lineMarkerBegin]] = ( lineMarkerBegin, lineMarkerEnd )
            lineMarkerBegin = lineMarkerEnd
