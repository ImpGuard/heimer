import re
from util import StringConstants

class RegexPatterns:
    """ Patterns used for parsing. Except when parsing options, names are considered simple words with underscores. """
    DELIMITER = re.compile(r"^delimiter\s+\"(.+)\"\s*(#.*)?$")
    OPTION = re.compile(r"^([\w]+)\s+([\w]+)\s+([\w]+)$")
    CLASS_NAME = re.compile(r"^[\w_]+$")
    FIELD = re.compile(r"^([\w_]+):(" + StringConstants.LIST_TYPE + r"\s*\(\s*([\w_]+)\s*\)|[\w_]+)(:([\w_]+|\+|\*)(\!)?)?\s*")

class ParserUtil:
    @staticmethod
    def lineStartsValidTag(line):
        return line == StringConstants.HEAD_TAG or \
            line == StringConstants.OPTIONS_TAG or \
            line == StringConstants.OBJECTS_TAG or \
            line == StringConstants.BODY_TAG

    @staticmethod
    def stripCommentsAndWhitespaceFromLine(line):
        firstInlineCommentIndex = line.find(StringConstants.INLINE_COMMENT)
        if firstInlineCommentIndex == -1:
            return line.strip()
        return line[:firstInlineCommentIndex].strip()

    @staticmethod
    def classDeclarationsAsString(classes):
        if len(classes) == 0:
            return ""
        result = ""
        for userClass in classes:
            result += "\n" + str(userClass)
        return result[1:]

    @staticmethod
    def fieldDeclarationsFromLine(line):
        fields = []
        fieldMatchResult = RegexPatterns.FIELD.match(line)
        while fieldMatchResult and len(fieldMatchResult.groups()) in [ 5, 6 ]:
            regexGroups = fieldMatchResult.groups()
            field = FieldDeclaration( regexGroups[0], regexGroups[1] )
            field.instanceRepetitionModeString = regexGroups[-2] if regexGroups[-2] else ""
            field.shouldSeparateInstancesByAdditionalNewline = regexGroups[-1] == StringConstants.SEPARATE_BY_ADDITIONAL_NEWLINE_MODE
            fields.append(field)
            line = line[fieldMatchResult.end():]
            fieldMatchResult = RegexPatterns.FIELD.match(line)
        if line.strip():
            # Unidentified tokens at end of line; invalidate field decls altogether.
            return []
        return fields

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
        self.instanceRepetitionModeString = ""
        self.shouldSeparateInstancesByAdditionalNewline = False

    def __str__(self):
        return str(( self.name, self.typeName, self.instanceRepetitionModeString,
            self.shouldSeparateInstancesByAdditionalNewline ))

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

class FormatFileObjectModel:

    def __init__(self):
        self.lineDelimiter = StringConstants.DEFAULT_SINGLE_LINE_DELIMITER
        self.commandLineOptions = []
        self.classes = []
        self.body = FieldDeclaration("body", "Body")

    def addCommandLineOption( self, flagName, variableName, optionType ):
        self.commandLineOptions.append(CommandLineOption( flagName, variableName, optionType ))

    def addClass( self, inputClass ):
        self.classes.append(inputClass)

    def __str__(self):
        result = ""
        if len(self.commandLineOptions):
            result += str([ str(option) for option in self.commandLineOptions ]) + "\n"
        if len(self.classes) > 0:
            result += ParserUtil.classDeclarationsAsString(self.classes) + "\n"
        return result[:-1]

class HeimerFormatFileParser:

    def __init__( self, formatFileName ):
        self.tagLineMarkerIntervals = {}
        self.failureMessages = []
        self.objectModel = FormatFileObjectModel()
        try:
            heimerFile = open( formatFileName, "r" )
            self.formatInputAsLines = [line.strip() for line in heimerFile.readlines()]
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
            currentStrippedLine = self.formatInputAsLines[lineMarker]
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
            currentStrippedLine = ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
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
            currentStrippedLine = ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                continue
            if not RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                return self.pushFailureMessage( "Expected class declaration.", lineMarker )
            classDecl = ClassDeclaration(currentStrippedLine)
            classDeclLineMarker = lineMarker
            while lineMarker < singleTagEndMarker - 1:
                lineMarker += 1
                currentStrippedLine = ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
                if not currentStrippedLine:
                    classDecl.addFieldsAsLine([])
                    continue
                if RegexPatterns.CLASS_NAME.match(currentStrippedLine):
                    lineMarker -= 1
                    break
                fields = ParserUtil.fieldDeclarationsFromLine(currentStrippedLine)
                if len(fields) == 0:
                    return self.pushFailureMessage( "Expected field declaration for \"%s\"" % (classDecl.name,), classDeclLineMarker, lineMarker )
                classDecl.addFieldsAsLine(fields)
            self.objectModel.addClass(classDecl)

    def parseBodyTag(self):
        if StringConstants.BODY_TAG not in self.tagLineMarkerIntervals:
            return
        bodyTagBeginMarker, bodyTagEndMarker = self.tagLineMarkerIntervals[StringConstants.BODY_TAG]
        hasBegunParsingFields = False
        body = ClassDeclaration("Body")
        for lineMarker in xrange( bodyTagBeginMarker + 1, bodyTagEndMarker ):
            currentStrippedLine = ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker])
            if not currentStrippedLine:
                if hasBegunParsingFields:
                    body.addFieldsAsLine(list())
                continue
            fields = ParserUtil.fieldDeclarationsFromLine(currentStrippedLine)
            if len(fields) == 0:
                return self.pushFailureMessage( "Expected field declaration for body.", lineMarker )
            body.addFieldsAsLine(fields)
            hasBegunParsingFields = True
        self.objectModel.addClass(body)

    def printFailures(self):
        for failureMessage in self.failureMessages:
            print failureMessage, "\n"

    def pushFailureMessage( self, message, *lineMarkers ):
        failureMessage = "Error: " + message
        for lineMarker in lineMarkers:
            failureMessage += "\n    at line " + str(lineMarker + 1) +  ":\t\"" + self.formatInputAsLines[lineMarker] + "\""
        self.failureMessages.append(failureMessage)

    def failureString(self):
        msg = ""
        for failureMessage in self.failureMessages:
            msg += failureMessage + "\n"
        return msg

    def parseFailed(self):
        return len(self.failureMessages) > 0

    def nextTagLocationFromLineMarker( self, marker ):
        while marker < len(self.formatInputAsLines):
            currentStrippedLine = ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[marker])
            if ParserUtil.lineStartsValidTag(currentStrippedLine):
                return marker
            marker += 1
        return len(self.formatInputAsLines)

    def firstLineMarkerWithText(self):
        marker = 0
        for line in self.formatInputAsLines:
            if ParserUtil.stripCommentsAndWhitespaceFromLine(line):
                return marker
            marker += 1
        return -1

    def computeTagIntervals(self):
        lineMarkerBegin = self.firstLineMarkerWithText()
        if lineMarkerBegin >= len(self.formatInputAsLines):
            return self.pushFailureMessage( "Input file empty or commented out." )
        if not ParserUtil.lineStartsValidTag(self.formatInputAsLines[lineMarkerBegin]):
            return self.pushFailureMessage( "Expected tag declaration.", lineMarkerBegin )
        lastTagName = None
        while lineMarkerBegin < len(self.formatInputAsLines):
            tagName = self.formatInputAsLines[lineMarkerBegin]
            if tagName in self.tagLineMarkerIntervals:
                return self.pushFailureMessage( "Duplicate tag name.", self.tagLineMarkerIntervals[tagName][0], lineMarkerBegin )
            lineMarkerEnd = self.nextTagLocationFromLineMarker(lineMarkerBegin + 1)
            lastTagName = self.formatInputAsLines[lineMarkerBegin]
            self.tagLineMarkerIntervals[lastTagName] = ( lineMarkerBegin, lineMarkerEnd )
            lineMarkerBegin = lineMarkerEnd
        if lastTagName:
            for lineMarker in xrange( len(self.formatInputAsLines) - 1, 0, -1 ):
                if ParserUtil.stripCommentsAndWhitespaceFromLine(self.formatInputAsLines[lineMarker]):
                    lineMarkerBegin, _ = self.tagLineMarkerIntervals[lastTagName]
                    self.tagLineMarkerIntervals[lastTagName] = lineMarkerBegin, lineMarker + 1
                    break
