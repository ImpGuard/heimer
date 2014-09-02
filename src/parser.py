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
    MULTIPLE_FIELD = re.compile(r"^(\w+):(" + StringConstants.LIST_TYPE + r"\s*\(\s*(\w+)\s*\)|\w+)(:(\w+|\+|\*)(\!)?)?$")
    BODY_VARIABLE = re.compile(r"^(\w+):(" + StringConstants.LIST_TYPE + r"\s*\(\s*(\w+)\s*\)|\w+)(:(\w+|\+|\*)(\!)?)?$")

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

    def __str__(self):
        return self.name

class CommandLineOption:

    def __init__( self, flagName, variableName, optionType ):
        self.flagName = flagName
        self.variableName = variableName
        self.optionType = optionType

    def __str__(self):
        return str(( self.flagName, self.variableName, str(self.optionType) ))

class Variable:

    def __init__( self, name, inputType ):
        self.name = name
        self.inputType = inputType
        self.instanceRepititionModeString = ""
        self.shouldSeparateInstancesByAdditionalNewline = False
        self.newlinesAfterLastInstance = 0

    def __str__(self):
        return str(( self.name, self.inputType, self.instanceRepititionModeString,
            self.shouldSeparateInstancesByAdditionalNewline, self.newlinesAfterLastInstance ))

class UserDefinedClass:

    def __init__( self, name, maySpanMultipleLines ):
        self.name = name
        self.fields = []
        self.maySpanMultipleLines = maySpanMultipleLines

    def addFieldFromVariable( self, variable ):
        self.fields.append(variable)

class HeimerFormat:

    def __init__(self):
        self.lineDelimiter = StringConstants.DEFAULT_SINGLE_LINE_DELIMITER
        self.commandLineOptions = []
        self.singleLineClasses = []
        self.multipleLineClasses = []
        self.variables = []

    def addCommandLineOption( self, flagName, variableName, optionType ):
        self.commandLineOptions.append(CommandLineOption( flagName, variableName, optionType ))

    def addSingleLineClass( self, inputClass ):
        self.singleLineClasses.append(inputClass)

    def addMultipleLineClass( self, inputClass ):
        self.multipleLineClasses.append(inputClass)

    def addVariable( self, variable ):
        self.variables.append(variable)

def makeVariableFromRegexGroups(groups):
    variable = Variable( groups[0], Type(groups[1]) )
    variable.instanceRepititionModeString = groups[-2] if groups[-2] else None
    variable.shouldSeparateInstancesByAdditionalNewline = groups[-1] == StringConstants.SEPARATE_BY_ADDITIONAL_NEWLINE_MODE
    return variable

class HeimerFormatFileParser:

    def __init__( self, formatFileName ):
        self.tagLineMarkerIntervals = {}
        self.failureMessages = []
        self.format = HeimerFormat()
        try:
            heimerFile = open( formatFileName, "r" )
            self.formatInputAsLines = heimerFile.read().split("\n")
            heimerFile.close()
        except IOError:
            return self.pushFailureMessage("Could not find file " + formatFileName + ".")
            self.formatInputAsLines = []
        self.computeTagIntervals()
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            self.pushFailureMessage("Input file requires a body tag.")
        self.parseAllTags()

    def parseAllTags(self):
        self.parseHeadTag()
        self.parseOptionsTag()
        self.parseSingleTag()
        self.parseMultipleTag()
        self.parseBodyTag()

    def parseHeadTag(self):
        if StringConstants.HEAD_TAG not in self.tagLineMarkerIntervals:
            return
        headTagBeginMarker, headTagEndMarker = self.tagLineMarkerIntervals[StringConstants.HEAD_TAG]
        for lineMarker in xrange( headTagBeginMarker + 1, headTagEndMarker ):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            delimiterMatchResults = RegexPatterns.DELIMITER.match(currentStrippedLine)
            if delimiterMatchResults is None:
                return self.pushFailureMessage( "Expected delimiter declaration.", lineMarker )
            self.format.lineDelimiter = delimiterMatchResults.group(1)

    def parseOptionsTag(self):
        if StringConstants.OPTIONS_TAG not in self.tagLineMarkerIntervals:
            return
        optionsTagBeginMarker, optionsTagEndMarker = self.tagLineMarkerIntervals[StringConstants.OPTIONS_TAG]
        for lineMarker in xrange( optionsTagBeginMarker + 1, optionsTagEndMarker ):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            optionsMatchResults = RegexPatterns.OPTION.match(currentStrippedLine)
            if optionsMatchResults is None:
                return self.pushFailureMessage( "Expected command line option.", lineMarker )
            optionType = Type(optionsMatchResults.group(3))
            if not optionType.isPrimitive():
                return self.pushFailureMessage( "Expected primitive type.", lineMarker )
            self.format.addCommandLineOption( optionsMatchResults.group(1), optionsMatchResults.group(2), optionType )

    def parseSingleTag(self):
        if StringConstants.SINGLE_TAG not in self.tagLineMarkerIntervals:
            return
        lineMarker, singleTagEndMarker = self.tagLineMarkerIntervals[StringConstants.SINGLE_TAG]
        while lineMarker < singleTagEndMarker - 1:
            lineMarker += 1
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            if not RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                return self.pushFailureMessage( "Expected class declaration.", lineMarker )
            singleLineClass = UserDefinedClass(currentStrippedLine, False)
            while lineMarker < singleTagEndMarker - 1:
                lineMarker += 1
                currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
                if not currentStrippedLine:
                    continue
                if RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                    lineMarker -= 1
                    break
                # HACK: We should change the field regex to not require this.
                currentStrippedLine += " "
                fieldMatchResults = RegexPatterns.SINGLE_FIELD.match(currentStrippedLine)
                while fieldMatchResults:
                    variable = Variable( fieldMatchResults.group(1), Type(fieldMatchResults.group(2)) )
                    singleLineClass.addFieldFromVariable(variable)
                    currentStrippedLine = currentStrippedLine[fieldMatchResults.end():]
                    fieldMatchResults = RegexPatterns.SINGLE_FIELD.match(currentStrippedLine)
                if currentStrippedLine.strip():
                    self.pushFailureMessage( "Expected field declaration.", lineMarker )
            self.format.addSingleLineClass(singleLineClass)

    def parseMultipleTag(self):
        if StringConstants.MULTIPLE_TAG not in self.tagLineMarkerIntervals:
            return
        lineMarker, multipleTagEndMarker = self.tagLineMarkerIntervals[StringConstants.MULTIPLE_TAG]
        while lineMarker < multipleTagEndMarker - 1:
            lineMarker += 1
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            if not RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                return self.pushFailureMessage( "Expected class declaration.", lineMarker )
            multipleLineClass = UserDefinedClass(currentStrippedLine, True)
            while lineMarker < multipleTagEndMarker - 1:
                lineMarker += 1
                currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
                if not currentStrippedLine:
                    continue
                if RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                    lineMarker -= 1
                    break
                fieldMatchResults = RegexPatterns.MULTIPLE_FIELD.match(currentStrippedLine)
                if not fieldMatchResults or len(fieldMatchResults.groups()) not in [ 5, 6 ]:
                    return self.pushFailureMessage( "Expected field declaration.", lineMarker )
                multipleLineClass.addFieldFromVariable(makeVariableFromRegexGroups(fieldMatchResults.groups()))
            self.format.addMultipleLineClass(multipleLineClass)

    def parseBodyTag(self):
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            return
        bodyTagBeginMarker, bodyTagEndMarker = self.tagLineMarkerIntervals[StringConstants.BODY_TAG]
        previousVariable = None
        for lineMarker in xrange( bodyTagBeginMarker + 1, bodyTagEndMarker ):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                if previousVariable:
                    previousVariable.newlinesAfterLastInstance += 1
                continue
            variableMatchResult = RegexPatterns.BODY_VARIABLE.match(currentStrippedLine)
            if not variableMatchResult:
                return self.pushFailureMessage( "Expected variable declaration.", lineMarker )
            previousVariable = makeVariableFromRegexGroups(variableMatchResult.groups())
            self.format.addVariable(previousVariable)
        if previousVariable:
            previousVariable.newlinesAfterLastInstance = 0

    def printFailures(self):
        print "========== %s FAILURES ==========" % (len(self.failureMessages))
        for failureMessage in self.failureMessages:
            print failureMessage, "\n"

    def pushFailureMessage( self, message, lineMarker=None ):
        failureMessage = "Error: " + message
        if lineMarker is not None:
            failureMessage += "\n  at line " + str(lineMarker) +  ": \"" + self.formatInputAsLines[lineMarker] + "\""
        self.failureMessages.append(failureMessage)

    def nextTagLocationFromLineMarker( self, marker ):
        while marker < len(self.formatInputAsLines):
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[marker])
            if lineStartsValidTag(currentStrippedLine):
                return marker
            marker += 1
        return len(self.formatInputAsLines)

    def firstLineMarkerWithText(self):
        marker = 0
        for line in self.formatInputAsLines:
            if stripCommentsAndWhitespaceFromLine(line):
                return marker
            marker += 1
        return -1

    def computeTagIntervals(self):
        lineMarkerBegin = self.firstLineMarkerWithText()
        if lineMarkerBegin >= len(self.formatInputAsLines):
            return self.pushFailureMessage( "Input file empty or commented out." )
        if not lineStartsValidTag(self.formatInputAsLines[lineMarkerBegin]):
            return self.pushFailureMessage( "Expected tag declaration.", lineMarkerBegin )
        while lineMarkerBegin < len(self.formatInputAsLines):
            if self.formatInputAsLines[lineMarkerBegin] in self.tagLineMarkerIntervals:
                return self.pushFailureMessage( "Duplicate tag name.", lineMarkerBegin )
            lineMarkerEnd = self.nextTagLocationFromLineMarker(lineMarkerBegin + 1)
            self.tagLineMarkerIntervals[self.formatInputAsLines[lineMarkerBegin]] = ( lineMarkerBegin, lineMarkerEnd )
            lineMarkerBegin = lineMarkerEnd
