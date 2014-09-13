from codegen import CodeGenerator
from parser import StringConstants
from converter import *
from optparse import OptionParser

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

    def generateHelperFunctions(self):
        """ Generate any helper functions that will be useful when parsing. """
        # Convert value to bool
        self._beginBlock("public static convertToBool(String name)")
        self._beginBlock("if (name.equals(\"1\") || name.toLowerCase().equals(\"true\"))")
        self.output.writeLine("return true;")
        self._endBlock()
        self._beginBlock("elif (name.equals(\"0\") || name.toLowerCase().equals(\"false\"))")
        self.output.writeLine("return = false;")
        self._endBlock()
        self.output.writeLine("throw new NumberFormatException();")
        self._endBlock()
        self.output.writeNewline()

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        if len(self.format.commandLineOptions()) == 0:
            return

        options = self.format.commandLineOptions()
        for option in options:
            self.output.writeLine("public static " + self._getTypeName(option.optionType) + " " + option.variableName + ";")
        self.output.writeNewline()

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
        self.output.write("String USAGE = \"" + helpMessage[0] + "\\n\"")
        for index, helpString in enumerate(helpMessage[1:]):
            self.output.writeNewline()
            if index == 0:
                self.output.indent()
            self.output.write(" + \"" + helpString + "\\n\"")
        self.output.writeLine(";")

        if len(helpMessage) > 1:
            self.output.dedent()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            return

        writeLine = self.output.writeLine
        options = self.format.commandLineOptions()

        # Create helper for code generation
        def handleOption( option, typeOfIf ):
            self._beginBlock(typeOfIf + " (args[i].equals(\"-" + option.flagName + "\"))")
            if isBool(option.optionType):
                writeLine(option.variableName + " = convertToBool(args[i + 1]);")
            else:
                writeLine(option.variableName + " = (" + self._getTypeName(option.optionType) + ") args[i + 1];")
            writeLine("i += 1;")
            self._endBlock()

        # Create option parser function
        self._beginBlock("private String parseOptions(String[] args)")
        self.generateHelpMessage()
        self._beginBlock("try")
        self._beginBlock("for ( int i = 0; i < args.length; i++ )")

        # generate code for handling each option type
        handleOption(options[0], "if")
        map( lambda opt: handleOption(opt, "elif"), options[1:] )

        # End of for loop
        self._endBlock()
        # End of try block
        self._endBlock()

        # Catch block
        self._beginBlock("catch (NumberFormatException e)")
        self.output.writeLine("System.out.println(USAGE);")
        self.output.writeLine("System.exit(1);")
        self._endBlock()

        # End of function
        self._endBlock()

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
        self.generateOptionVariables()
        self.generateHelperFunctions()
        self.generateOptionParserFunction()
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

