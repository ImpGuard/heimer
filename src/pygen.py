from codegen import CodeGenerator
from convert import *
import util
import pygenStatic

StringConstants = util.StringConstants

class PythonGenerator(CodeGenerator):
    
    def writeLine( self, line ):
        self.currentFile.writeLine(line)

    def writeNewLine(self):
        self.currentFile.writeNewLine()

    def comment( self, line ):
        self.currentFile.comment(line)

    def initialize(self):
        """ Perform additional initialization if required. """
        self.util.filename += ".py"
        self.data.filename += ".py"

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateDataFileHeader(self):
        """ For generating the data file header, such as the import statements. """
        raise NotImplementedError()

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of 
        fields (in order) of that class. """
        self._beginBlock("class %s:")
        self._beginBlock("def __init__(self):")
        # Initialize each field to be None
        for f in fields:
            self.writeLine("self.%s = None" % f.name())
        self._endBlock()
        self._endBlock()
        self.writeNewLine

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        pass

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        primitiveParsers =  pygenStatic.getPrimitiveParsers()
        self.write(primitiveParsers)

    def generateClassParserFunction( self, className, lines ):
        """ For generating the helper functions for parsing a user defined class. The first argument
        is the class name and the second argument is a list of FormatLine's. """
        # The name of the class parser should be "parseX" where X is the class name.
        # The argument to the parser should be the list of lines to be parsed and the current
        # line counter.
        # If parsed successfully, the parser should return a X object and the new line counter.
        self._beginBlock("def parse%s( lines, currentLineNumber ):" % className)
        self.writeLine("userClass = %s()" % className)
        self.writeLine("lineNumber = currentLineNumber")

        def handleEmptyLine(line):
            self.comment("Parsing empty line")
            self.writeLine("fields = lines[lineNumber].split()")
            self._beginBlock("if len(fields) > 0:")
            self.writeLine("raise Exception('Parser Error on line %d: line is not empty when it \
                should be.') % (lineNumber)")
            self._endBlock()
            self.writeLine("lineNumber += 1")

        def handleSimpleLine(line):
            # The case where there is only one primitve field that is not a list.
            if line.numFields() == 1 and line.getField(0).isPrimitive() and not line.getField(0).isList():
                field = line.getField(0)
                self.writeLine("userClass.%s = %s( line[lineNumber], lineNumber )" % ( field.name(), \
                    self.typeNameToParseFuncName[field.typeName()] ))
            # The case where ther is only one list primitive field.
            elif line.numFields() == 1 and line.getField(0).isPrimitive() and line.getField(0).isList():
                field = line.getField(0)
                listType = "list(%s)" % field.typeName
                self.writeLine("line = lines[lineNumber].split('%s')" % self.format.lineDelimiter())
                self.writeLine("userClass.%s = %s( line[lineNumber], lineNumber )" % ( field.name(), \
                    self.typeNameToParseFuncName[field.typeName()] ))
            # The case where there is only one non-primitive field.
            elif line.numFields() == 1 and not line.getField(0).isPrimitive():
                field = line.getField(0)
            # The case where there is multiple fields on a line.
            else:
                pass
            self.writeLine("lineNumber += 1")

        def handleRepeatingLine(line):
            pass

        for line in lines:
            self._generateLineParserFunction(line)

        self._endBlock()
    

    def _generateLineParserFunction( self, line ):
        """ For generating the helper functions for parsing a line in the input file. """
        self.writeLine("line = remainingLines[lineNumber]")
        self.writeLine("line = line.split('%s')" % self.format.lineDelimiter())
        if line.isZeroOrMoreRepetition() or line.isOneOrMoreRepetition():
            sdd 
        elif line.isIntegerRepetition() or line.isVariableRepetition():
            ss

        self.writeNewLine()


    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        pass

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        if len(self.format.commandLineOptions()) == 0:
            return
        for opt in self.format.commandLineOptions():
            self.writeLine("%s = None" % opt.variableName)
        self.writeNewLine()


    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            return
        self._beginBlock("def %s(*args):" % CodeGenerator.PARSE_OPTIONS)
        self.comment("A function for parsing command line arguments. The options will be stored in \
            global variables, while the left over positional arguments are returned as a list.")

        options = self.format.commandLineOptions()
        self.writeLine("USAGE = 'usage: %prog [options] input_file_name'")
        self.writeLine("optParser = OptionParser(usage = USAGE)")
        
        variableNames = []
        for opt in options:
            variableNames.append(opt.variableName)
            self.writeLine("optParser.add_option('-%s', action='store', dest='%s')" % 
                ( opt.flagName, opt.variableName ))
        self.writeLine("( options, remainingArgs ) = optParser.parse_args(args)")
        self.writeLine("global " + ", ".join(variableNames))
        map( lambda name: self.writeLine("%s = options.%s" % ( name, name )), variableNames )
        self.writeLine("return remainingArgs")

        self._endBlock()
        self.writeNewLine()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        raise NotImplementedError()

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        raise NotImplementedError()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        raise NotImplementedError()


    def generateFileHeader(self):
        """ For generating the file header, such as the import statements. """
        writeLine("from optparse import OptionParser")


    def generateHelperFunctions(self):
        """ Generate any helper functions that will be useful when parsing. """
        pass

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        pass # FIXME

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        pass # FIXME

    def generateMain(self):
        """ For generating the empty main method that the user can fill in. """
        pass # FIXME

    def _beginBlock( self, line ):
        self.writeLine(line)
        self.indent()

    def _endBlock(self):
        self.dedent()
