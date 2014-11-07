from codegen import CodeGenerator
from converter import *
from util import StringConstants
from pygenStatic import pygenStaticHelpers

class PythonGenerator(CodeGenerator):

    def write( self, line ):
        self.currentFile.write(line)

    def writeLine( self, line ):
        self.currentFile.writeLine(line)

    def writeNewline(self):
        self.currentFile.writeNewline()

    def comment( self, line ):
        self.currentFile.comment(line)

    def writeImportLine( self, line ):
        self.currentFile.writeImportLine(line)

    def beginBlock( self, line ):
        self.writeLine(line)
        self.currentFile.indent()

    def endBlock(self):
        self.currentFile.dedent()

    def initialize(self):
        """ Perform additional initialization if required. """
        self.util.filename += ".py"
        self.data.filename += ".py"

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateDataFileHeader(self):
        """ For generating the data file header, such as the import statements. """
        self.writeLine("#!/usr/bin/env python")
        self.writeNewline()

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of
        fields (in order) of that class. """
        self.beginBlock("class %s:" % className)
        self.beginBlock("def __init__(self):")
        # Initialize each field to be None
        for f in fields:
            self.writeLine("self.%s = None" % f.name())
        self.endBlock()
        self.endBlock()
        self.writeNewline()

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        self.writeLine("#!/usr/bin/env python")
        self.writeNewline()
        self.writeImportLine("import " + CodeGenerator.DATA_FILE_NAME)
        self.writeNewline()

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        helpers =  pygenStaticHelpers()
        self.write(helpers)
        self.writeNewline()

    def generateClassParserFunction( self, className, lines ):
        """ For generating the helper functions for parsing a user defined class. The first argument
        is the class name and the second argument is a list of FormatLine's. """
        # The name of the class parser should be "parseX" where X is the class name.
        # The argument to the parser should be the input file to be parsed ,the current
        # line number and the position of the current line in the input file.
        # If parsed successfully, the parser should return a X object, the new line number and position.
        self.beginBlock("def parse%s( inputFile, currentLineNumber, currentLinePos ):" % className)
        self.writeLine("userClass = %s.%s()" % ( CodeGenerator.DATA_FILE_NAME, className ))
        self.writeNewline()

        def handleEmptyLine():
            self.comment("Parsing empty line")
            self.writeLine("fields = readline(inputFile).split()")
            self.beginBlock("if len(fields) > 0:")
            self.writeLine("raise ValueError('Parser Error on line %d: line is not empty when it " + \
                "should be.' % (currentLineNumber))")
            self.endBlock()
            self.writeLine("currentLineNumber += 1")
            self.writeLine("currentLinePos = inputFile")

        def handleSimpleLine(line):
            # The case where there is only one primitve field that is not a list.
            if line.numFields() == 1 and line.getField(0).isPrimitive() and not line.getField(0).isList():
                field = line.getField(0)
                self.writeLine("userClass.%s = %s( readline(inputFile), currentLineNumber )" % \
                    ( field.name(), self.typeNameToParseFuncName[field.typeName()] ))
                self.writeLine("currentLineNumber += 1")
                self.writeLine("currentLinePos = inputFile.tell()")
            # The case where ther is only one list primitive field.
            elif line.numFields() == 1 and line.getField(0).isPrimitive() and line.getField(0).isList():
                field = line.getField(0)
                listType = "list(%s)" % field.listType()
                self.writeLine("fields = readline(inputFile).split('%s')" % self.format.lineDelimiter())
                self.writeLine("userClass.%s = %s( fields, currentLineNumber )" % ( field.name(), self.typeNameToParseFuncName[listType] ))
                self.writeLine("currentLineNumber += 1")
                self.writeLine("currentLinePos = inputFile.tell()")
            # The case where there is only one non-primitive field.
            elif line.numFields() == 1 and not line.getField(0).isPrimitive():
                field = line.getField(0)
                self.writeLine("userClass.%s, currentLineNumber, currentLinePos = %s( inputFile, currentLineNumber, currentLinePos )" % ( field.name(), self.typeNameToParseFuncName[field.typeName()] ))
            # The case where there is multiple fields on a line. The fields are all primitives.
            else:
                self.writeLine("fields = readline(inputFile).split('%s')" % self.format.lineDelimiter())
                # If the last field is not a list, then the number of fields should match exactly
                if not line.getField(-1).isList():
                    self.beginBlock("if len(fields) != %d:" % line.numFields())
                    self.writeLine("raise ValueError('Parser Error on line %d: Expecting " + \
                        str(line.numFields()) + " fields (%d found).' % ( currentLineNumber, len(fields) ))")
                    self.endBlock()
                # Else there should be at least X fields on the line, where X is the number of fields
                # on the line in the format file
                else:
                    self.beginBlock("if len(fields) < %d:" % (line.numFields()))
                    self.writeLine("raise ValueError('Parser Error on line %d: Expecting " + \
                        str(line.numFields()) + " fields (%d found).' % ( currentLineNumber, len(fields) ))")
                    self.endBlock()
                for i, field in enumerate(line):
                    if field.isList():
                        listType = "list(%s)" % field.listType()
                        self.writeLine("userClass.%s = %s( fields[%d:], currentLineNumber )" % ( \
                            field.name(), self.typeNameToParseFuncName[field.typeName()], i ))
                    else:
                        self.writeLine("userClass.%s = %s( fields[%d], currentLineNumber )" % ( \
                            field.name(), self.typeNameToParseFuncName[field.typeName()], i ))
                self.writeLine("currentLineNumber += 1")
                self.writeLine("currentLinePos = inputFile.tell()")

        def handleRepeatingLine(line):
            field = line.getField(0)
            self.writeLine("userClass.%s = []" % field.name())

            if line.isZeroOrMoreRepetition() or line.isOneOrMoreRepetition():
                self.beginBlock("try:")
                self.beginBlock("while True:")
                # Field is an user defined class.
                if not field.isPrimitive():
                    self.writeLine("retObj, currentLineNumber, currentLinePos = %s( inputFile, currentLineNumber, currentLinePos )" % self.typeNameToParseFuncName[field.typeName()])
                # Field is a non-list primitive.
                elif field.isPrimitive() and not field.isList():
                    self.writeLine("retObj = %s( readline(inputFile), currentLineNumber )" % \
                        self.typeNameToParseFuncName[field.typeName()])
                    self.writeLine("currentLineNumber += 1")
                    self.writeLine("currentLinePos = inputFile.tell()")
                # Field is a list primitive.
                else:
                    listType = "list(%s)" % field.listType()
                    self.writeLine("fields = readline(inputFile).split(%s)" % self.format.lineDelimiter())
                    self.writeLine("retObj = %s( fields, currentLineNumber )" % \
                        self.typeNameToParseFuncName[listType])
                    self.writeLine("currentLineNumber += 1")
                    self.writeLine("currentLinePos = inputFile.tell()")
                self.writeLine("userClass.%s.append(retObj)" % field.name())
                if line.isSplitByNewline():
                    self.writeLine("prevLineNumber = currentLineNumber")
                    self.writeLine("prevLinePos = currentLinePos")
                    handleEmptyLine()
                self.endBlock()
                self.endBlock()

                self.beginBlock("except ( ValueError, EOFError ) as e:")
                if line.isOneOrMoreRepetition():
                    self.beginBlock("if len(userClass.%s) < 1:" % field.name())
                    self.writeLine("raise ValueError('Parser Error on line %d: Expecting at least 1 " + \
                        field.typeName() + " objects (0 found)' % currentLineNumber)")
                    self.endBlock()
                if line.isSplitByNewline():
                    self.writeLine("currentLineNumber = prevLineNumber")
                    self.writeLine("currentLinePos = prevLinePos")
                self.writeLine("inputFile.seek(currentLinePos)")
                self.endBlock()

            elif line.isIntegerRepetition() or line.isVariableRepetition():
                numRepetition = line.repetitionAmountString()
                if line.isVariableRepetition():
                    numRepetition = "userClass." + numRepetition

                self.beginBlock("try:")
                self.beginBlock("for _index in xrange(%s):" % numRepetition)
                # Field is an user defined class.
                if not field.isPrimitive():
                    self.writeLine("retObj, currentLineNumber, currentLinePos = %s( inputFile, currentLineNumber, currentLinePos )" % self.typeNameToParseFuncName[field.typeName()])
                # Field is a non-list primitive.
                elif field.isPrimitive() and not field.isList():
                    self.writeLine("retObj = %s( readline(inputFile), currentLineNumber )" % \
                        self.typeNameToParseFuncName[field.typeName()])
                    self.writeLine("currentLineNumber += 1")
                    self.writeLine("currentLinePos = inputFile.tell()")
                # Field is a list primitive.
                else:
                    listType = "list(%s)" % field.listType()
                    self.writeLine("fields = readline(inputFile).split(%s)" % self.format.lineDelimiter())
                    self.writeLine("retObj = %s( fields, currentLineNumber )" % \
                        self.typeNameToParseFuncName[listType])
                    self.writeLine("currentLineNumber += 1")
                self.writeLine("userClass.%s.append(retObj)" % field.name())
                if line.isSplitByNewline():
                    self.beginBlock("if _index + 1 < %s:" % numRepetition)
                    handleEmptyLine()
                    self.endBlock()
                self.endBlock()
                self.endBlock()

                self.beginBlock("except ValueError as e:")
                self.writeLine("raise ValueError('Parser Error on line %d: Expecting %d " + \
                    field.typeName() + " objects (%d found)' % ( currentLineNumber, " + numRepetition + \
                        ", _index ))")
                self.endBlock()

        def handleLine(line):
            if line.isEmpty():
                handleEmptyLine()
            elif line.isRepeating():
                handleRepeatingLine(line)
            else:
                handleSimpleLine(line)

        for line in lines:
            handleLine(line)
            self.writeNewline()

        self.writeLine("return userClass, currentLineNumber, currentLinePos")
        self.endBlock()
        self.writeNewline()

    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        self.writeLine("#!/usr/bin/env python")
        self.writeNewline()
        self.writeImportLine("import " + CodeGenerator.UTIL_FILE_NAME)
        self.writeLine("from optparse import OptionParser")
        self.writeImportLine("import sys")
        self.writeNewline()

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        self.writeLine("%s = None" % CodeGenerator.USER_ARGS)
        for opt in self.format.commandLineOptions():
            self.writeLine("%s = None" % opt.variableName)
        self.writeNewline()


    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        self.beginBlock("def %s(commandLineArguments):" % CodeGenerator.PARSE_OPTIONS)
        self.comment("A function for parsing command line arguments. The options will be stored in")
        self.comment("global variables, while the left over positional arguments are stored in the")
        self.comment("global variable %s." % CodeGenerator.USER_ARGS)

        options = self.format.commandLineOptions()
        self.writeLine("USAGE = 'usage: %prog [options] input_file_name'")
        self.writeLine("optParser = OptionParser(usage = USAGE)")

        variableNames = []
        for opt in options:
            variableNames.append(opt.variableName)
            self.writeLine("optParser.add_option('-%s', action='store', dest='%s')" %
                ( opt.flagName, opt.variableName ))
        self.writeLine("global %s" % CodeGenerator.USER_ARGS)
        self.writeLine("( options, %s ) = optParser.parse_args(commandLineArguments)" % CodeGenerator.USER_ARGS)
        if len(variableNames) > 0:
            self.writeLine("global " + ", ".join(variableNames))
            map( lambda name: self.writeLine("%s = options.%s" % ( name, name )), variableNames )
        self.endBlock()
        self.writeNewline()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        self.beginBlock("def %s( inputFile ):" % CodeGenerator.PARSE_INPUT)
        self.beginBlock("try:")
        self.writeLine("body, lineNumber, linePos = %s.%s( inputFile, 1, 0 )" % ( CodeGenerator.UTIL_FILE_NAME, self.typeNameToParseFuncName[self.bodyTypeName] ))

        self.writeLine("line = inputFile.readline()")
        self.beginBlock("while line != '':")
        self.beginBlock("if line.strip() != '':")
        self.writeLine("sys.stderr.write('Parser Error on line %d: Finished parsing but did not reach end of file.' % lineNumber)")
        self.writeLine("exit(1)")
        self.endBlock()
        self.writeLine("lineNumber += 1")
        self.writeLine("line = inputFile.readline()")
        self.endBlock()


        self.writeLine("return body")
        self.endBlock()

        self.beginBlock("except ValueError as e:")
        self.writeLine("sys.stderr.write(str(e))")
        self.writeLine("exit(1)")
        self.endBlock()
        self.beginBlock("except EOFError as e:")
        self.writeLine("sys.stderr.write('Parser Error: Reached end of file before finished parsing.')")
        self.writeLine("exit(1)")
        self.endBlock()

        self.endBlock()
        self.writeNewline()

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        self.beginBlock("def %s(commandLineArguments):" % CodeGenerator.RUN)
        self.writeLine("%s(commandLineArguments[1:])" % CodeGenerator.PARSE_OPTIONS)
        self.beginBlock("try:")
        self.beginBlock("if len(%s) == 0:" % CodeGenerator.USER_ARGS)
        self.writeLine("sys.stderr.write('Parser Error: Require input file name.')")
        self.writeLine("exit(1)")
        self.endBlock()
        self.writeLine("filename = %s[0]" % CodeGenerator.USER_ARGS)
        self.writeLine("inputFile = open(filename, 'r')")
        self.writeLine("return %s(inputFile)" % CodeGenerator.PARSE_INPUT)
        self.endBlock()
        self.beginBlock("except IOError as e:")
        self.writeLine("sys.stderr.write('Parser Error: Problem opening file, %s' % e)" )
        self.writeLine("exit(1)")
        self.endBlock()
        self.beginBlock("except Exception as e:")
        self.writeLine("sys.stderr.write('Parser Error: %s' % e)")
        self.writeLine("import traceback")
        self.writeLine("traceback.print_exc()")
        self.writeLine("exit(1)")
        self.endBlock()

        self.endBlock()
        self.writeNewline()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        self.beginBlock("if __name__ == '__main__':")
        self.writeLine("body = %s(sys.argv)" % CodeGenerator.RUN)
        self.endBlock()

