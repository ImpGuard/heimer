import re

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

class RegexPatterns:

    DELIMITER = re.compile(r"^delimiter\s+\"(.+)\"$")
    OPTION = re.compile(r"^(\w+)\s+(\w+)\s+(\w+)$")
    CLASS_NAME = re.compile(r"^\w+$")
    SINGLE_FIELD = re.compile(r"^(\w+):(" + StringConstants.LIST_TYPE + r"\s*\(\s*(\w+)\s*\)|\w+)\s+")

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
        return line.strip()
    return line[:firstInlineCommentIndex].strip()

class Type:

    def __init__( self, rawName ):
        # Remove whitespace from the raw name.
        # FIXME: Do not allow types such as "s tri ng" to be parsed.
        self.name = "".join(rawName.split())

    def isInteger(self):
        return self.name == StringConstants.INTEGER_TYPE

    def isFloat(self):
        return self.name == StringConstants.FLOAT_TYPE

    def isString(self):
        return self.name == StringConstants.STRING_TYPE

    def isBool(self):
        return self.name == StringConstants.BOOL_TYPE

    def isList(self):
        return self.name.find(StringConstants.LIST_TYPE) == 0 and \
            self.name[len(StringConstants.LIST_TYPE)] == "(" and \
            self.name[-1] == ")"

    def listType(self):
        return Type(self.name[ len(StringConstants.LIST_TYPE) : len(self.name) - 1 ]) if self.isList() else None

    def isPrimitive(self):
        return self.isInteger() or self.isFloat() or self.isString() or self.isBool()

class CommandLineOption:

    def __init__( self, flagName, variableName, optionType ):
        self.flagName = flagName
        self.variableName = variableName
        self.optionType = optionType

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

    def __init__( self, delimiter=StringConstants.DEFAULT_SINGLE_LINE_DELIMITER ):
        self.lineDelimiter = delimiter

class OptionsTag:

    def __init__(self):
        self.commandLineOptions = []

    def addCommandLineOption( self, flagName, variableName, optionType ):
        self.commandLineOptions.append(CommandLineOption( flagName, variableName, optionType ))

class SingleTag:

    def __init__( self, lineDelimiter=StringConstants.DEFAULT_SINGLE_LINE_DELIMITER ):
        self.classes = []
        self.lineDelimiter = lineDelimiter

    def addUserDefinedInputClass( self, inputClass ):
        self.classes.append(inputClass)

class MultipleTag:

    def __init__(self):
        self.classes = []

    def addUserDefinedInputClass( self, inputClass ):
        self.classes.append(inputClass)

class BodyTag:

    def __init__(self):
        self.globalVariables = []

    def addGlobalVariable( self, globalVariable ):
        self.globalVariables.append(globalVariable)

class HeimerInputFileParser:

    def __init__( self, inputFileName ):
        self.tagLineMarkerIntervals = {}
        self.failureMessage = ""
        self.failed = False
        try:
            heimerFile = open( inputFileName, "r" )
            self.inputAsLines = heimerFile.read().split("\n")
            heimerFile.close()
        except IOError:
            self.failParsingWithMessage("Could not find file " + inputFileName + ".")
            self.inputAsLines = []
        self.computeTagIntervals()
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            self.failParsingWithMessage("Input file requires a body tag.")

    def headTag(self):
        headTag = HeadTag()
        if StringConstants.HEAD_TAG not in self.tagLineMarkerIntervals:
            return headTag
        headTagBeginMarker, headTagEndMarker = self.tagLineMarkerIntervals[StringConstants.HEAD_TAG]
        for lineMarker in xrange( headTagBeginMarker + 1, headTagEndMarker ):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.inputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            delimiterMatchResults = RegexPatterns.DELIMITER.match(currentStrippedLine)
            if delimiterMatchResults is None:
                return self.failParsingWithMessage("Expected delimiter declaration.", lineMarker)
            headTag.lineDelimiter = delimiterMatchResults.group(1)
        return headTag

    def optionsTag(self):
        optionsTag = OptionsTag()
        if StringConstants.OPTIONS_TAG not in self.tagLineMarkerIntervals:
            return optionsTag
        optionsTagBeginMarker, optionsTagEndMarker = self.tagLineMarkerIntervals[StringConstants.OPTIONS_TAG]
        for lineMarker in xrange( optionsTagBeginMarker + 1, optionsTagEndMarker ):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.inputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            optionsMatchResults = RegexPatterns.OPTION.match(currentStrippedLine)
            if optionsMatchResults is None:
                return self.failParsingWithMessage("Expected command line option.", lineMarker)
            optionType = Type(optionsMatchResults.group(3))
            if not optionType.isPrimitive():
                return self.failParsingWithMessage("Expected primitive type.", lineMarker)
            optionsTag.addCommandLineOption( optionsMatchResults.group(1), optionsMatchResults.group(2), optionType )
        return optionsTag

    def singleTag(self):
        singleTag = SingleTag()
        if StringConstants.SINGLE_TAG not in self.tagLineMarkerIntervals:
            return singleTag
        lineMarker, singleTagEndMarker = self.tagLineMarkerIntervals[StringConstants.SINGLE_TAG]
        while lineMarker < singleTagEndMarker - 1:
            lineMarker += 1
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.inputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            if not RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                return self.failParsingWithMessage("Expected class declaration.", lineMarker)
            singleLineClass = UserDefinedInputClass(currentStrippedLine, False)
            while lineMarker < singleTagEndMarker - 1:
                lineMarker += 1
                currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.inputAsLines[lineMarker])
                if not currentStrippedLine:
                    continue
                # HACK: We should change the field regex to not require this.
                currentStrippedLine += " "
                fieldMatchResults = RegexPatterns.SINGLE_FIELD.match(currentStrippedLine)
                while fieldMatchResults:
                    variable = Variable( fieldMatchResults.group(1), Type(fieldMatchResults.group(2)) )
                    singleLineClass.addFieldFromVariable(variable)
                    currentStrippedLine = currentStrippedLine[fieldMatchResults.end():]
                    fieldMatchResults = RegexPatterns.SINGLE_FIELD.match(currentStrippedLine)
                if currentStrippedLine.strip():
                    self.failParsingWithMessage("Expected field declaration.", lineMarker)
            singleTag.addUserDefinedInputClass(singleLineClass)
        return singleTag

    def failParsingWithMessage( self, message, lineMarker=None ):
        if not self.failed:
            self.failed = True
            self.failureMessage = "Error: " + message
            if lineMarker is not None:
                self.failureMessage += "\n  at line " + str(lineMarker) +  ": \"" + self.inputAsLines[lineMarker] + "\""
        return None

    def nextTagLocationFromLineMarker( self, marker ):
        while marker < len(self.inputAsLines):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.inputAsLines[marker])
            if lineStartsValidTag(currentStrippedLine):
                return marker
            marker += 1
        return len(self.inputAsLines)

    def firstLineMarkerWithText(self):
        marker = 0
        for line in self.inputAsLines:
            if stripCommentsAndWhitespaceFromLine(line):
                return marker
            marker += 1
        return -1

    def computeTagIntervals(self):
        lineMarkerBegin = self.firstLineMarkerWithText()
        if lineMarkerBegin >= len(self.inputAsLines):
            return self.failParsingWithMessage("Input file empty or commented out.")
        if not lineStartsValidTag(self.inputAsLines[lineMarkerBegin]):
            return self.failParsingWithMessage("Expected tag declaration.", lineMarkerBegin)
        while lineMarkerBegin < len(self.inputAsLines):
            if self.inputAsLines[lineMarkerBegin] in self.tagLineMarkerIntervals:
                return self.failParsingWithMessage("Duplicate tag name.", lineMarkerBegin)
            lineMarkerEnd = self.nextTagLocationFromLineMarker(lineMarkerBegin + 1)
            self.tagLineMarkerIntervals[self.inputAsLines[lineMarkerBegin]] = ( lineMarkerBegin, lineMarkerEnd )
            lineMarkerBegin = lineMarkerEnd
