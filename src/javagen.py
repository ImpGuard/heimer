from codegen import CodeGenerator
from javagenStatic import *
from util import *

from optparse import OptionParser
import os

""" Class for generating Java code. """
class JavaGenerator(CodeGenerator):

    def initialize(self):
        """ Perform additional initialization if required. """
        self.output.setExtension("java")
        self.util.setExtension("java")
        self.classFiles = []

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateUtilFile()
        self.generateMainFile()
        self.generateClasses()
        self.output.save()
        self.util.save()
        map(lambda c: c.save(), self.classFiles)

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of
        fields (in order) of that class. """
        classFile = HeimerFile(className + ".java")
        self.classFiles.append(classFile)

        self.currentFile = classFile

        self._beginBlock("public " + className )
        for field in fields:
            classFile.writeLine("public " + self._getTypeName(field) + " " + field.name() + ";")

        self._endBlock()

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFile(self):
        """ Generate helper functions in the separate util file. """
        self.currentFile = self.util
        self.generateUtilFileHeader()
        self.generateHelperFunctions()

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        # Import library headers
        self.currentFile.writeLine("import java.util.ArrayList;")
        self.currentFile.writeNewline()

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        self._beginBlock("public class " + CodeGenerator.UTIL_FILE_NAME)

        helpers = staticHelpers()
        helpers.replace("\t", HeimerFile.indentString)
        map(lambda s: self.currentFile.writeLine(s), helpers.splitlines())

        self._endBlock()

    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFile(self):
        """ Generate main file where the main function resides. """
        self.currentFile = self.output
        self.generateMainFileHeader()
        self._beginBlock("public class " + os.path.splitext(os.path.basename(self.currentFile.filename))[0])
        self.generateOptionVariables()
        self.generateMainFunction()
        self.generateRunFunction()
        self.generateOptionParserFunction()
        self.generateInputParserFunction()
        self._endBlock()

    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        # Import library headers
        self.currentFile.writeLine("import java.util.ArrayList;")
        self.currentFile.writeNewline()

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        self.currentFile.writeLine("public static ArrayList<String> "+ CodeGenerator.USER_ARGS +" = new ArrayList<String>();")

        if len(self.format.commandLineOptions()) == 0:
            return

        options = self.format.commandLineOptions()
        for option in options:
            self.currentFile.writeLine("public static " + self._getBasicTypeName(option.optionType) + " " + option.variableName + ";")
        self.currentFile.writeNewline()

    def generateHelpMessage(self):
        # Create option parser and generate helpMessage strings
        optParse = OptionParser(usage = "usage: %prog [options] input_file_name")
        for option in self.format.commandLineOptions():
            optParse.add_option( "-" + option.flagName, action="store", dest = option.variableName,
                    help = "<Insert your help message here>")

        helpMessageList = optParse.format_help().strip().splitlines()
        if len(helpMessageList) == 0:
            return

        # Condense newlines and store result in helpMessage
        helpMessage = []
        for helpString in helpMessageList:
            if helpString == "":
                helpMessage[-1] += "\\n"
                continue
            helpMessage.append(helpString)

        # Generate the help message multiline string
        self.currentFile.write("String USAGE = \"" + helpMessage[0] + "\\n\"")
        for index, helpString in enumerate(helpMessage[1:]):
            self.currentFile.writeNewline()
            if index == 0:
                self.currentFile.indent()
            self.currentFile.write(" + \"" + helpString + "\\n\"")
        self.currentFile.writeLine(";")

        if len(helpMessage) > 1:
            self.currentFile.dedent()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            return

        writeLine = self.currentFile.writeLine
        options = self.format.commandLineOptions()

        # Create helper for code generation
        def handleOption( option, typeOfIf ):
            self._beginBlock(typeOfIf + " (args[i].equals(\"-" + option.flagName + "\"))")
            if isBool(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_BOOL + "(args[i + 1]);")
            elif isInteger(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_INT + "(args[i + 1]);")
            elif isFloat(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_FLOAT + "(args[i + 1]);")
            else:
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_STRING + "(args[i + 1]);")
            writeLine("i += 1;")
            self._endBlock()

        # Create option parser function
        self._beginBlock("private static void " + CodeGenerator.PARSE_OPTIONS + "(String[] args)")
        self.generateHelpMessage()
        self._beginBlock("try")
        self._beginBlock("for ( int i = 0; i < args.length; i++ )")

        # generate code for handling each option type
        handleOption(options[0], "if")
        map( lambda opt: handleOption(opt, "else if"), options[1:] )

        # generate code for handling extraneous inputs
        self._beginBlock("else")
        writeLine(CodeGenerator.USER_ARGS + ".add(args[i]);")
        self._endBlock()

        # End of for loop
        self._endBlock()
        # End of try block
        self._endBlock()

        # Catch block
        self._beginBlock("catch (NumberFormatException e)")
        self.output.writeLine("System.out.println(USAGE);")
        self.output.writeLine("System.exit(1);")
        self._endBlock()

        # generate code for returning the filename
        self._beginBlock("if (" + CodeGenerator.USER_ARGS + ".size() == 0)")
        writeLine("System.out.println(USAGE);")
        writeLine("System.exit(1);")
        self._endBlock()

        # End of function
        self._endBlock()
        self.currentFile.writeNewline()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        pass

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        self._beginBlock("public static void " + CodeGenerator.RUN + "(String[] args)")
        self.output.writeLine(CodeGenerator.PARSE_OPTIONS + "(args);")
        self._endBlock()
        self.output.writeNewline()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        self._beginBlock("public static void main(String[] args)")
        self.output.writeLine(CodeGenerator.RUN + "(args);")
        self._endBlock()
        self.output.writeNewline()

    ################################################################################
    # Helper Functions
    ################################################################################

    def _getBasicTypeName( self, typeName ):
        if isInteger(typeName):
            return "Integer"
        elif isString(typeName):
            return "String"
        elif isBool(typeName):
            return "Boolean"
        elif isList(typeName):
            return "ArrayList<" + getBasicTypeName(listType(typeName)) + ">"
        else:
            return None


    def _getTypeName( self, field ):
        typeName = self._getBasicTypeName(field.typeName())
        if typeName != None:
            return typeName

        if field.isClassList():
            return "ArrayList<" + field.typeName() + ">"
        else:
            return field.typeName()

    def _beginBlock( self, line ):
        self.currentFile.writeLine(line)
        self.currentFile.writeLine("{")
        self.currentFile.indent()

    def _endBlock(self):
        self.currentFile.dedent()
        self.currentFile.writeLine("}")
