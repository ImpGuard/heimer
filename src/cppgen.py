from codegen import CodeGenerator
from cppgenStatic import *
from util import *

from optparse import OptionParser
from os.path import join, splitext, basename

""" Class for generating CPP code. """
class CPPGenerator(CodeGenerator):

    def initialize(self):
        """ Perform additional initialization if required. """
        self.output.setExtension("cpp")
        self.util.setExtension("h")
        self.data.setExtension("h")

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateDataFile(self):
        """ Generate classes in a separate data file. """
        CodeGenerator.generateDataFile(self);
        self.currentFile.writeLine("#endif")

    def generateDataFileHeader(self):
        """ For generating the data file header, such as the import statements. """
        writeLine = self.currentFile.writeLine
        writeNewline = self.currentFile.writeNewline
        writeLine("#ifndef %s_H" % CodeGenerator.DATA_FILE_NAME.upper())
        writeLine("#define %s_H" % CodeGenerator.DATA_FILE_NAME.upper())
        writeNewline()
        writeLine("#include <vector>")
        writeLine("#include <string>")
        writeNewline()

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of
        fields (in order) of that class. """
        self.typeNameToParseFuncName[className] = "parse%s" % className
        self._beginBlock("struct " + className )
        for field in fields:
            self.currentFile.writeLine(self._getTypeName(field) + " " + field.name() + ";")
        self._endBlock(";")
        self.currentFile.writeNewline()

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFile(self):
        self.currentFile = self.util
        self.generateUtilFileHeader()
        self._beginBlock("namespace " + CodeGenerator.PARSER_NAME)
        self.generateHelperFunctions()
        self.generateClassParserFunctions()
        self._endBlock()

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        # Import library headers
        self.currentFile.writeLine("#include <vector>")
        self.currentFile.writeLine("#include <sstream>")
        self.currentFile.writeLine("#include <string>")
        self.currentFile.writeLine("#include <cctype>")
        self.currentFile.writeLine("#include <stdexcept>")
        self.currentFile.writeLine("#include <fstream>")
        self.currentFile.writeNewline()

        # Import data header
        self.currentFile.writeLine("#include \"" + self.data.filename + "\"")

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        # Static helpers for primitives
        helpers = cppgenStaticHelpers()
        map(lambda s: self.currentFile.writeLine(s), helpers.splitlines())
        self.currentFile.writeNewline()

    def generateClassParserFunction( self, className, lines ):
        """ For generating a helper functions for parsing a user defined class. The first argument
        is the class name and the second argument is a list of FormatLine's. """
        writeLine = self.currentFile.writeLine
        write = self.currentFile.write

        def isSimplePrimitive(field):
            return field.isInteger() or field.isFloat() or field.isString() or field.isBool()

        def generateSetup():
            # include std in all parser functions
            writeLine("using namespace std;")

            # Helper to do some setup in every parser function
            writeLine(className + " result;")
            didSplit = False
            didRepeat = False
            didRepeatPlus = False

            for line in lines:
                didRepeat = didRepeat or line.isRepeating()
                didRepeatPlus = didRepeatPlus or  line.isOneOrMoreRepetition()
                didSplit = didSplit or line.numFields() > 1 or (not line.isEmpty() and line.getField(0).isList())

            if didSplit:
                writeLine("vector<string> fields;")
            if didRepeat:
                writeLine("streampos prevFilePos = getFilePointer(f);")
                writeLine("int prevLineNumber = lineNumber;")
            if didRepeatPlus:
                writeLine("bool didRepeatOnce = false;")

        def handleEmptyLine():
            # Handle the empty line case
            self._beginBlock("if (!trim(readLine(f)).compare(\"\") == 0)")
            writeLine("stringstream err;")
            writeLine("err << \"Parser Error on line \"  << lineNumber << " +
                "\": Should be an empty line\";")
            writeLine("throw invalid_argument(err.str());")
            self._endBlock()
            writeLine("lineNumber += 1;")

        def handleSimpleLineOneField(field):
            # Helper for handleSimpleLine
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f), lineNumber);")
                writeLine("lineNumber += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = split(readLine(f), \"" + self.format.lineDelimiter() + "\");")
                write("result." + field.name() + " = "
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()] + "(fields, lineNumber);")
                writeLine("lineNumber += 1;")
            else:
                # Field is a class, recurse
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName[field.typeName()] + "(f, lineNumber);")

        def handleSimpleLineMultipleField(index, field):
            # Helper for handleSimpleLine
            if isSimplePrimitive(field):
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName[field.typeName()]
                    + "(fields[" + str(index) + "], lineNumber);")
            elif field.isPrimitive():
                # Field is primitive list, use rest of fields)
                # FIXME WRONG
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()]
                    + "(copyRange(fields, " + str(index) + ", fields.size()), lineNumber);")
            else:
                # Field is a class? Cannot be!
                raise Exception("This should never happen.")

            writeLine("lineNumber += 1;")

        def handleSimpleLine(line):
            if line.numFields() == 1:
                # Only one field, no need to split unnecessarily
                handleSimpleLineOneField(line.getField(0))
            else:
                # Multiple fields, split it
                writeLine("fields = split(readLine(f), \"" + self.format.lineDelimiter() + "\");")
                if (line.getField(-1).isList()):
                    self._beginBlock("if (fields.size() < " + str(line.numFields()) + ")")
                else:
                    self._beginBlock("if (fields.size() != " + str(line.numFields()) + ")")
                writeLine("stringstream err;")
                writeLine("err << \"Parser Error on line \" << lineNumber << " +
                    "\": Expecting " + str(line.numFields()) + " fields (\" << fields.size() << \" found)\";")
                writeLine("throw invalid_argument(err.str());")
                self._endBlock()
                for index, field in enumerate(line):
                    handleSimpleLineMultipleField(index, field)

        def handleRepeatingLineForField(field):
            # Helper for handleRepeating
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + ".push_back("
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f), lineNumber));")
                writeLine("lineNumber += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = split(readLine(f), \"" + self.format.lineDelimiter() + "\");")
                writeLine("result." + field.name() + ".push_back("
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()] + "(fields, lineNumber));")
                writeLine("lineNumber += 1;")
            else:
                # Field is a class, recurse
                writeLine("result." + field.name() + ".push_back("
                    + self.typeNameToParseFuncName[field.typeName()] + "(f, lineNumber));")

        def handleRepeatingLine(line):
            # Must be a primitive or class repeated
            if line.isIntegerRepetition() or line.isVariableRepetition():
                # Constant repetition amount
                field = line.getField(0)
                # Generate the repetition string
                repetitionString = ""
                if line.isIntegerRepetition():
                    repetitionString = str(line.repetitionAmountString())
                else:
                    repetitionString =  "result." + line.repetitionAmountString()
                # Begin loop
                self._beginBlock("for (int i = 0; i < " + repetitionString + "; i++)")
                # Main handler
                handleRepeatingLineForField(field)
                # Check for newline
                if (line.isSplitByNewline()):
                    self._beginBlock("if (i != " + repetitionString + " - 1)")
                    handleEmptyLine()
                    self._endBlock()
                # End loop
                self._endBlock()
            elif line.isZeroOrMoreRepetition():
                field = line.getField(0)
                # Wrap with try block
                self._beginBlock("try")
                # Save initial position
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber;")
                # Begin infinite loop
                self._beginBlock("while (true)")
                # Main handler
                handleRepeatingLineForField(field)
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber;")
                # Check for newline
                if (line.isSplitByNewline()):
                    handleEmptyLine()
                # End infinite loop and try block
                self._endBlock()
                self._endBlock()
                # Catch any errors, reset line number and continue
                self._beginBlock("catch (...)")
                writeLine("seek(f, prevFilePos);")
                writeLine("lineNumber = prevLineNumber;")
                self._endBlock()
            elif line.isOneOrMoreRepetition:
                field = line.getField(0)
                # Wrap with try block
                self._beginBlock("try")
                # Initialize object and checker to ensure at least one repetition
                writeLine("didRepeatOnce = false;")
                # Begin infinite loop
                self._beginBlock("while (true)")
                # Main handler
                handleRepeatingLineForField(field)
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber;")
                writeLine("didRepeatOnce = true;")
                # Check for newline
                if (line.isSplitByNewline()):
                    handleEmptyLine()
                # End infinite loop and try block
                self._endBlock()
                self._endBlock()
                # Catch any errors, either (1) reset line number and continue (2) error if did not repeat once
                self._beginBlock("catch (...)")
                self._beginBlock("if (!didRepeatOnce)")
                writeLine("stringstream err;")
                writeLine("err << \"Parser Error on line \" << lineNumber << " +
                    "\": Expecting at least 1 " + field.typeName() + " (0 found)\";")
                writeLine("throw invalid_argument(err.str());")
                self._endBlock()
                writeLine("seek(f, prevFilePos);")
                writeLine("lineNumber = prevLineNumber;")
                self._endBlock()
            else:
                raise Exception("This should never happen.")


        self._beginBlock(className + " parse" + className + "(std::ifstream& f, int& lineNumber)")
        generateSetup()

        # Handle the three different cases, helpers are inner functions defined above
        for line in lines:
            if line.isEmpty():
                handleEmptyLine()
            elif line.isRepeating():
                handleRepeatingLine(line)
            else:
                handleSimpleLine(line)

        writeLine("return result;")
        self._endBlock()
        self.currentFile.writeNewline()

    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFile(self):
        """ Generate main file where the main function resides. """
        self.currentFile = self.output
        self.generateMainFileHeader()
        self.generateHelpMessage()
        self.generateOptionVariables()
        self.generateForwardDeclarations()
        self.generateMainFunction()
        self.generateRunFunction()
        self.generateOptionParserFunction()
        self.generateInputParserFunction()


    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        # Import library headers
        self.currentFile.writeLine("#include <vector>")
        self.currentFile.writeLine("#include <string>")
        self.currentFile.writeLine("#include <stdexcept>")
        self.currentFile.writeLine("#include <fstream>")
        self.currentFile.writeLine("#include <iostream>")
        self.currentFile.writeNewline()
        # Import data and util headers
        self.currentFile.writeLine("#include \"" + self.data.filename + "\"")
        self.currentFile.writeLine("#include \"" + self.util.filename + "\"")
        self.currentFile.writeNewline()

    def generateForwardDeclarations(self):
        self.currentFile.writeLine("bool " + CodeGenerator.RUN + "(int, char**, " + self.bodyTypeName + "&);")
        self.currentFile.writeLine("void " + CodeGenerator.PARSE_OPTIONS + "(std::vector<std::string>);")
        self.currentFile.writeLine("bool " + CodeGenerator.PARSE_INPUT + "(std::ifstream&, " + self.bodyTypeName + "&);")
        self.currentFile.writeNewline()

    def generateHelpMessage(self):
        # Create option parser and generate helpMessage strings
        optParse = OptionParser(usage = "usage: ./scriptname [options] input_file_name")
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
        self.currentFile.write("std::string USAGE = \"" + helpMessage[0] + "\\n\"")
        for index, helpString in enumerate(helpMessage[1:]):
            self.currentFile.writeNewline()
            if index == 0:
                self.currentFile.indent()
            self.currentFile.write("\"" + helpString + "\\n\"")
        self.currentFile.writeLine(";")

        if len(helpMessage) > 1:
            self.currentFile.dedent()

        self.currentFile.writeNewline()

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        self.currentFile.writeLine("std::vector<std::string> "+ CodeGenerator.USER_ARGS +";")

        if len(self.format.commandLineOptions()) == 0:
            return

        options = self.format.commandLineOptions()
        for option in options:
            self.currentFile.writeLine(self._getBasicTypeName(option.optionType) + " " + option.variableName + ";")
        self.currentFile.writeNewline()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        self._beginBlock("int main(int argc, char** argv)")
        self.currentFile.writeLine(self.bodyTypeName + " " + CodeGenerator.PARSED_OBJ + ";")
        self.currentFile.writeLine(CodeGenerator.RUN + "(argc, argv, " + CodeGenerator.PARSED_OBJ + ");")
        self._endBlock()
        self.currentFile.writeNewline()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            # Just handle extraneous inputs
            self._beginBlock("void " + CodeGenerator.PARSE_OPTIONS + "(std::vector<std::string> args)")
            self.currentFile.writeLine(CodeGenerator.USER_ARGS + " = args[i];")
            self._endBlock()
            return

        writeLine = self.currentFile.writeLine
        options = self.format.commandLineOptions()

        # Create helper for code generation
        def handleOption( option, typeOfIf ):
            self._beginBlock(typeOfIf + " (args[i].compare(\"-" + option.flagName + "\") == 0)")
            if isBool(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.PARSER_NAME + "::" + CodeGenerator.PARSE_BOOL + "(args[i + 1], fakeLineNumber);")
            elif isInteger(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.PARSER_NAME + "::" + CodeGenerator.PARSE_INT + "(args[i + 1], fakeLineNumber);")
            elif isFloat(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.PARSER_NAME + "::" + CodeGenerator.PARSE_FLOAT + "(args[i + 1], fakeLineNumber);")
            else:
                writeLine(option.variableName + " = " + CodeGenerator.PARSER_NAME + "::" + CodeGenerator.PARSE_STRING + "(args[i + 1], fakeLineNumber);")
            writeLine("i += 1;")
            self._endBlock()

        # Create option parser function
        self._beginBlock("void " + CodeGenerator.PARSE_OPTIONS + "(std::vector<std::string> args)")
        writeLine("using namespace std;")
        self._beginBlock("try")
        writeLine("int fakeLineNumber = -1;")
        self._beginBlock("for ( int i = 0; i < args.size(); i++ )")

        # generate code for handling each option type
        handleOption(options[0], "if")
        map( lambda opt: handleOption(opt, "else if"), options[1:] )

        # generate code for handling extraneous inputs
        self._beginBlock("else")
        writeLine(CodeGenerator.USER_ARGS + ".push_back(args[i]);")
        self._endBlock()

        # End of for loop
        self._endBlock()
        # End of try block
        self._endBlock()

        # Catch block
        self._beginBlock("catch (const invalid_argument& e)")
        self.output.writeLine("cerr << USAGE << endl;")
        self.output.writeLine("exit(1);")
        self._endBlock()

        # generate code for returning the filename
        self._beginBlock("if (" + CodeGenerator.USER_ARGS + ".size() == 0)")
        writeLine("cerr << USAGE << endl;")
        writeLine("exit(1);")
        self._endBlock()

        # End of function
        self._endBlock()
        self.currentFile.writeNewline()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        writeLine = self.currentFile.writeLine
        # Begin function declaration
        self._beginBlock("bool " + CodeGenerator.PARSE_INPUT + "(std::ifstream &f, " + self.bodyTypeName + " &result)")
        writeLine("using namespace std;")

        # Setup line number
        writeLine("int lineNumber = 0;")

        # Main try block
        self._beginBlock("try")
        writeLine("result = " + CodeGenerator.PARSER_NAME + "::parse" + self.bodyTypeName + "(f, lineNumber);")
        writeLine("string line;")
        self._beginBlock("while (getline(f, line))")
        self._beginBlock("if (!" + CodeGenerator.PARSER_NAME + "::trim(line).compare(\"\") == 0)")
        writeLine("throw runtime_error(\"Parser Error: Did not reach end of file\");")
        self._endBlock()
        self._endBlock()
        writeLine("return true;")
        self._endBlock()

        # Begin catch end of file
        self._beginBlock("catch (int e)")
        writeLine("cerr << \"Parser Error: Reached end of file before finished parsing\";")
        writeLine("exit(1);")
        self._endBlock()

        # Begin other exception catches
        self._beginBlock("catch (invalid_argument& ia)")
        writeLine("cerr << ia.what() << endl;")
        writeLine("exit(1);")
        self._endBlock()
        self._beginBlock("catch (runtime_error& re)")
        writeLine("cerr << re.what() << endl;")
        writeLine("exit(1);")
        self._endBlock()

        writeLine("cerr << \"Unknown error occurred\" << endl;")
        writeLine("exit(1);")

        # End function declaration
        self._endBlock()

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        writeLine = self.currentFile.writeLine

        self._beginBlock("bool " + CodeGenerator.RUN + "(int argc, char** argv, " + self.bodyTypeName + "& result)")

        writeLine("using namespace std;")

        # Convert argv to a vector
        writeLine("vector<string> args;")
        self._beginBlock("for (int i = 1; i < argc; i++)")
        writeLine("args.push_back(string(argv[i]));")
        self._endBlock()

        # Parse Options
        writeLine(CodeGenerator.PARSE_OPTIONS + "(args);")

        # Parse input file if it exists
        self._beginBlock("if (" + CodeGenerator.USER_ARGS + ".size() != 0)")
        writeLine("string filename = " + CodeGenerator.USER_ARGS + "[0];")
        # Try to parse the file
        writeLine("ifstream f(filename.c_str(), ios_base::in);")
        self._beginBlock("if (f.fail())")
        writeLine("cerr << \"Could not open '\" + filename + \"'\" << endl;")
        self._endBlock()
        writeLine(CodeGenerator.PARSE_INPUT + "(f, result);")
        writeLine("f.close();")
        writeLine("return true;")
        # File not found!
        self._endBlock()
        # Otherwise error
        self._beginBlock("else")
        writeLine("cerr << USAGE << endl;");
        writeLine("exit(1);")
        self._endBlock()

        writeLine("return false;")

        self._endBlock()
        self.currentFile.writeNewline()

    ################################################################################
    # Helper Functions
    ################################################################################

    def _getBasicTypeName( self, typeName ):
        if isInteger(typeName):
            return "int"
        elif isString(typeName):
            return "std::string"
        elif isBool(typeName):
            return "bool"
        elif isList(typeName):
            return "std::vector<" + self._getBasicTypeName(listType(typeName)) + ">"
        else:
            return None


    def _getTypeName( self, field ):
        typeName = self._getBasicTypeName(field.typeName())
        if typeName == None:
            typeName = field.typeName()

        if field.isRepeating():
            return "std::vector<" + typeName + ">"
        else:
            return typeName

    def _beginBlock( self, line ):
        self.currentFile.writeLine(line)
        self.currentFile.writeLine("{")
        self.currentFile.indent()

    def _endBlock(self, semicolon = False):
        self.currentFile.dedent()
        self.currentFile.writeLine("}" + (";" if semicolon else ""))
