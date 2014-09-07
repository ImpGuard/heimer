from codegen import CodeGenerator
from parser import StringConstants
from converter import *

""" Class for generating Java code. """
class JavaGenerator(CodeGenerator):

    def generateFileHeader(self):
        """ For generating the file header, such as the import statements. """
        # Import library headers
        self.output.writeLine("import java.util.Scanner")
        # Import class files
        for (className, fields) in self.format.classes():
            self.output.writeLine("import " + className)
        self.output.writeNewline()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            return

        writeLine = self.output.writeLine
        options = self.format.commandLineOptions()

        # Create global variables
        for option in options:
            writeLine("public static " + self._getTypeName(option.optionType) + " " + option.variableName + ";")
        self.output.writeNewline()

        # Create parser function
        self._beginBlock("private String parseOptions(String[] args)")
        self._beginBlock("for ( int i = 0; i < args.length; i++ )")
        self._beginBlock("if (args[i].equals(\"-" + options[0].flagName + "\")")
        writeLine(options[0].variableName + " = (" + self._getTypeName(options[0].optionType) + ") args[i + 1];")
        writeLine("i += 1;")
        self._endBlock()
        for option in options[1:]:
            self._beginBlock("else if (args[i].equals(\"-" + option.flagName + "\")")
            writeLine(option.variableName + " = (" + self._getTypeName(option.optionType) + ") args[i + 1];")
            writeLine("i += 1;")
            self._endBlock()
        self._endBlock()
        self._endBlock()

    def generateClassParserFunctions(self):
        """ For generating the functions to parse an input file, eating up the lines associated with
        each user specified class. """
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

    def generateClass( self, className, fieldNamesAndTypes ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a dictionary
        containing key-value pairs of the form (field name, field type), both as strings. """
        pass # FIXME

    def generateMainClass(self):
        """ Helper to generate the main class that wraps the parsers. """
        self.generateFileHeader()
        self._beginBlock("public class Main")
        self.generateOptionParserFunction()
        self.generateClassParserFunctions()
        self.generateInputParserFunction()
        self.generateMain()
        self._endBlock()

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateClasses()
        self.generateMainClass()
        self.output.save()

    def _beginBlock( self, line ):
        self.output.writeLine(line)
        self.output.writeLine("{")
        self.output.indent()

    def _endBlock(self):
        self.output.dedent()
        self.output.writeLine("}")

    def _getTypeName( self, typeName ):
        if isInteger(typeName):
            return "Integer"
        elif isString(typeName):
            return "String"
        elif isBool(typeName):
            return "Boolean"
        elif isList(typeName):
            return "ArrayList<" + _getTypeName(listType(typeName)) + ">"
