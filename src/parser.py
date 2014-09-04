import re

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

class RegexPatterns:

    # FIXME: Handle underscores in variable names.
    DELIMITER = re.compile(r"^delimiter\s+\"(.+)\"$")
    OPTION = re.compile(r"^(\w+)\s+(\w+)\s+(\w+)$")
    CLASS_NAME = re.compile(r"^\w+$")
    FIELD = re.compile(r"^(\w+):(" + StringConstants.LIST_TYPE + r"\s*\(\s*(\w+)\s*\)|\w+)(:(\w+|\+|\*)(\!)?)?\s*")

def lineStartsValidTag(line):
    return line == StringConstants.HEAD_TAG or \
        line == StringConstants.OPTIONS_TAG or \
        line == StringConstants.OBJECTS_TAG or \
        line == StringConstants.BODY_TAG

def stripCommentsAndWhitespaceFromLine(line):
    # FIXME: Allow using "#" as a separator in <head> tag.
    firstInlineCommentIndex = line.find(StringConstants.INLINE_COMMENT)
    if firstInlineCommentIndex == -1:
        return line.strip()
    return line[:firstInlineCommentIndex].strip()

class CommandLineOption:

    def __init__( self, flagName, variableName, optionType ):
        self.flagName = flagName
        self.variableName = variableName
        self.optionType = optionType

    def __str__(self):
        return str(( self.flagName, self.variableName, str(self.optionType) ))

class FieldDeclaration:

    def __init__( self, name, typeName ):
        self.name = name
        self.typeName = typeName
        self.instanceRepititionModeString = ""
        self.shouldSeparateInstancesByAdditionalNewline = False
        self.newlinesAfterLastInstance = 0

    def __str__(self):
        return str(( self.name, self.typeName, self.instanceRepititionModeString,
            self.shouldSeparateInstancesByAdditionalNewline, self.newlinesAfterLastInstance ))

class ClassDeclaration:

    def __init__( self, name ):
        self.name = name
        self.lines = []

    def addFieldsAsLine( self, fields ):
        self.lines.append(fields)

    def __str__(self):
        result = "class " + self.name + "\n"
        for line in self.lines:
            result += "  -"
            for field in line:
                result += "  " + str(field)
            result += "\n"
        return result[:-1]

class HeimerObjectModel:

    def __init__(self):
        self.lineDelimiter = StringConstants.DEFAULT_SINGLE_LINE_DELIMITER
        self.commandLineOptions = []
        self.classes = []
        self.body = ClassDeclaration("Body")

    def addCommandLineOption( self, flagName, variableName, optionType ):
        self.commandLineOptions.append(CommandLineOption( flagName, variableName, optionType ))

    def addClass( self, inputClass ):
        self.classes.append(inputClass)

    def __str__(self):
        result = ""
        if len(self.commandLineOptions):
            result += str([ str(option) for option in self.commandLineOptions ]) + "\n"
        if len(self.classes) > 0:
            result += userDefinedClassesAsString(self.classes) + "\n"
        result += str(self.body)
        return result

def userDefinedClassesAsString(classes):
    if len(classes) == 0:
        return ""
    result = ""
    for userClass in classes:
        result += "\n" + str(userClass)
    return result[1:]

def fieldDeclarationsFromLine(line):
    fields = []
    fieldMatchResult = RegexPatterns.FIELD.match(line)
    while fieldMatchResult and len(fieldMatchResult.groups()) in [ 5, 6 ]:
        regexGroups = fieldMatchResult.groups()
        field = FieldDeclaration( regexGroups[0], regexGroups[1] )
        field.instanceRepititionModeString = regexGroups[-2] if regexGroups[-2] else ""
        field.shouldSeparateInstancesByAdditionalNewline = regexGroups[-1] == StringConstants.SEPARATE_BY_ADDITIONAL_NEWLINE_MODE
        fields.append(field)
        line = line[fieldMatchResult.end():]
        fieldMatchResult = RegexPatterns.FIELD.match(line)
    if line.strip():
        # Unidentified tokens at end of line; invalidate field decls altogether.
        return []
    return fields

class HeimerFormatFileParser:

    def __init__( self, formatFileName ):
        self.tagLineMarkerIntervals = {}
        self.failureMessages = []
        self.objectModel = HeimerObjectModel()
        try:
            heimerFile = open( formatFileName, "r" )
            self.formatInputAsLines = heimerFile.read().split("\n")
            heimerFile.close()
        except IOError:
            return self.pushFailureMessage("Could not find file " + formatFileName + ".")
            self.formatInputAsLines = []
        self.computeTagIntervals()
        if len(self.failureMessages) > 0:
            return
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            return self.pushFailureMessage("Input file requires a body tag.")
        self.parseAllTags()

    def parseAllTags(self):
        self.parseHeadTag()
        self.parseOptionsTag()
        self.parseObjectsTag()
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
            self.objectModel.lineDelimiter = delimiterMatchResults.group(1)

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
            optionType = optionsMatchResults.group(3)
            self.objectModel.addCommandLineOption( optionsMatchResults.group(1), optionsMatchResults.group(2), optionType )

    def parseObjectsTag(self):
        if StringConstants.OBJECTS_TAG not in self.tagLineMarkerIntervals:
            return
        lineMarker, singleTagEndMarker = self.tagLineMarkerIntervals[StringConstants.OBJECTS_TAG]
        while lineMarker < singleTagEndMarker - 1:
            lineMarker += 1
            currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            if not RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                return self.pushFailureMessage( "Expected class declaration.", lineMarker )
            classDecl = ClassDeclaration(currentStrippedLine)
            classDeclLineMarker = lineMarker
            while lineMarker < singleTagEndMarker - 1:
                lineMarker += 1
                currentStrippedLine = stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
                if not currentStrippedLine:
                    continue
                if RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                    lineMarker -= 1
                    break
                fields = fieldDeclarationsFromLine(currentStrippedLine)
                if len(fields) == 0:
                    return self.pushFailureMessage( "Expected field declaration for \"%s\"" % (classDecl.name,), classDeclLineMarker, lineMarker )
                classDecl.addFieldsAsLine(fields)
            self.objectModel.addClass(classDecl)

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
            fields = fieldDeclarationsFromLine(currentStrippedLine)
            if len(fields) == 0:
                return self.pushFailureMessage( "Expected field declaration for body.", lineMarker )
            previousVariable = fields[-1]
            self.objectModel.body.addFieldsAsLine(fields)
        if previousVariable:
            previousVariable.newlinesAfterLastInstance = 0

    def printFailures(self):
        for failureMessage in self.failureMessages:
            print failureMessage, "\n"

    def pushFailureMessage( self, message, *lineMarkers ):
        failureMessage = "Error: " + message
        for lineMarker in lineMarkers:
            failureMessage += "\n    at line " + str(lineMarker + 1) +  ":\t\"" + self.formatInputAsLines[lineMarker] + "\""
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
            tagName = self.formatInputAsLines[lineMarkerBegin]
            if tagName in self.tagLineMarkerIntervals:
                return self.pushFailureMessage( "Duplicate tag name.", self.tagLineMarkerIntervals[tagName][0], lineMarkerBegin )
            lineMarkerEnd = self.nextTagLocationFromLineMarker(lineMarkerBegin + 1)
            self.tagLineMarkerIntervals[self.formatInputAsLines[lineMarkerBegin]] = ( lineMarkerBegin, lineMarkerEnd )
            lineMarkerBegin = lineMarkerEnd
