from codegen import CodeGenerator
from cppgenStatic import *
from util import *

from optparse import OptionParser
from os.path import join, splitext, basename

""" Class for generating CPP code. """
class CPPGenerator(CodeGenerator):

    def initialize(self):
        """ Perform additional initialization if required. """
        InstaParseFile.commentString = "//"
        self.main.setExtension("cpp")
        self.util.setExtension("h")
        self.data.setExtension("h")

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateDataFile(self):
        """ Generate classes in a separate data file. """
        self.currentFile = self.data
        self.currentFile.writeLine("#ifndef %s_H" % CodeGenerator.DATA_FILE_NAME.upper())
        self.currentFile.writeLine("#define %s_H" % CodeGenerator.DATA_FILE_NAME.upper())
        self.currentFile.writeNewline()
        CodeGenerator.generateDataFile(self);
        self.currentFile.writeLine("#endif")

    def generateDataFileHeader(self):
        """ For generating the data file header, such as the import statements. """
        writeLine = self.currentFile.writeLine
        writeNewline = self.currentFile.writeNewline
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
        self.currentFile.writeLine("#ifndef %s_H" % CodeGenerator.UTIL_FILE_NAME.upper())
        self.currentFile.writeLine("#define %s_H" % CodeGenerator.UTIL_FILE_NAME.upper())
        self.generateUtilFileHeader()
        self._beginBlock("namespace " + CodeGenerator.PARSER_NAME)
        self.generateHelperFunctions()
        self.generateClassParserFunctions()
        self._endBlock()
        self.currentFile.writeLine("#endif")

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
        self.currentFile.writeLine("#include \"" + CodeGenerator.DATA_FILE_NAME + ".h" + "\"")

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
            self._beginBlock("if (!(trim(readLine(f, \"" + className + "\")).compare(\"\") == 0))")
            writeLine("stringstream err;")
            writeLine("err << \"Parser Error on line \"  << lineNumber << " +
                "\": Should be an empty line.\";")
            writeLine("throw invalid_argument(err.str());")
            self._endBlock()
            writeLine("lineNumber += 1;")

        def handleSimpleLineOneField(field):
            # Helper for handleSimpleLine
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f, \"" + className + "\"), lineNumber);")
                writeLine("lineNumber += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = split(readLine(f, \"" + className + "\"), \"" + self.format.lineDelimiter() + "\");")
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
                writeLine("fields = split(readLine(f, \"" + className + "\"), \"" + self.format.lineDelimiter() + "\");")
                if (line.getField(-1).isList()):
                    self._beginBlock("if (fields.size() < " + str(line.numFields()) + ")")
                else:
                    self._beginBlock("if (fields.size() != " + str(line.numFields()) + ")")
                writeLine("stringstream err;")
                writeLine("err << \"Parser Error on line \" << lineNumber << " +
                    "\": Expecting " + str(line.numFields()) + " fields (\" << fields.size() << \" found).\";")
                writeLine("throw invalid_argument(err.str());")
                self._endBlock()
                for index, field in enumerate(line):
                    handleSimpleLineMultipleField(index, field)

        def handleRepeatingLineForField(field):
            # Helper for handleRepeating
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + ".push_back("
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f, \"" + className + "\"), lineNumber));")
                writeLine("lineNumber += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = split(readLine(f, \"" + className + "\"), \"" + self.format.lineDelimiter() + "\");")
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
                # Wrap handler with try
                self._beginBlock("try")
                # Main handler
                handleRepeatingLineForField(field)
                # Check for newline
                if (line.isSplitByNewline()):
                    self._beginBlock("if (i != " + repetitionString + " - 1)")
                    handleEmptyLine()
                    self._endBlock()
                # End try
                self._endBlock()
                # Catch any error to throw appropriate error message
                self._beginBlock("catch (...)")
                writeLine("stringstream err;")
                writeLine("err << \"Parser Error on line \" << lineNumber << "
                    + "\": Expecting exactly \" << " + repetitionString + " << \" \\\"" + field.typeName()
                    + "\\\" when parsing \\\"" + className + "." + field.name()
                    + "\\\" (\" << i << \" found).\";")
                writeLine("throw runtime_error(err.str());")
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
                writeLine("err << \"Parser Error on line \" << lineNumber << "
                    + "\": Expecting at least 1 \\\"" + field.typeName()
                    + "\\\" when parsing \\\"" + className + "." + field.name()
                    + "\\\" (0 found).\";")
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
        self.currentFile = self.main
        self.generateMainFileHeader()
        self.generateForwardDeclarations()
        self.generateMainFunction()
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
        self.currentFile.writeLine("#include \"" + CodeGenerator.DATA_FILE_NAME + ".h" + "\"")
        self.currentFile.writeLine("#include \"" + CodeGenerator.UTIL_FILE_NAME + ".h" + "\"")
        self.currentFile.writeNewline()

    def generateForwardDeclarations(self):
        self.currentFile.writeLine(self.bodyTypeName + " " + CodeGenerator.PARSE_INPUT + "(const std::string &filename);")
        self.currentFile.writeNewline()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        self._beginBlock("int main(int argc, char** argv)")
        self.currentFile.comment("Call " + CodeGenerator.PARSE_INPUT + "(filename) to parse the file of that name.")
        self._endBlock()
        self.currentFile.writeNewline()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        writeLine = self.currentFile.writeLine
        # Begin function declaration
        self._beginBlock(self.bodyTypeName + " " + CodeGenerator.PARSE_INPUT + "(const std::string &filename)")
        writeLine("using namespace std;")

        # Open file
        writeLine("ifstream f(filename.c_str(), ios_base::in);")
        self._beginBlock("if (f.fail())")
        writeLine("cerr << \"Could not open \\\"\" + filename + \"\\\".\" << endl;")
        writeLine("exit(1);")
        self._endBlock()

        # Main try block
        self._beginBlock("try")
        # Initial setup
        writeLine("int lineNumber = 1;")
        writeLine(self.bodyTypeName + " result = "
            + CodeGenerator.PARSER_NAME + "::" + self.typeNameToParseFuncName[self.bodyTypeName] + "(f, lineNumber);")
        # Handle trailing newlines
        writeLine("string line;")
        self._beginBlock("while (getline(f, line))")
        self._beginBlock("if (!" + CodeGenerator.PARSER_NAME + "::trim(line).compare(\"\") == 0)")
        writeLine("stringstream err;");
        writeLine("err << \"Parser Error on line\" << lineNumber << \": Finished parsing but did not reach end of file.\";")
        writeLine("throw runtime_error(err.str());")
        self._endBlock()
        self._endBlock()
        writeLine("return result;")
        self._endBlock()

        # Catch parser errors
        self._beginBlock("catch (invalid_argument& ia)")
        writeLine("cerr << ia.what() << endl;")
        writeLine("exit(1);")
        self._endBlock()
        # Catch parser errors
        self._beginBlock("catch (runtime_error& re)")
        writeLine("cerr << re.what() << endl;")
        writeLine("exit(1);")
        self._endBlock()
        # Catch all other errors
        self._beginBlock("catch (...)")
        writeLine("cerr << \"Unknown error occurred.\" << endl;")
        writeLine("exit(1);")
        self._endBlock()

        # Should never reach this line
        writeLine("cerr << \"Unknown error occurred.\" << endl;")
        writeLine("exit(1);")

        # End function declaration
        self._endBlock()

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
            space = ""
            if isList(field.typeName()):
                space = " "
            return "std::vector<" + typeName + space + ">"
        else:
            return typeName

    def _beginBlock( self, line ):
        self.currentFile.writeLine(line)
        self.currentFile.writeLine("{")
        self.currentFile.indent()

    def _endBlock(self, semicolon = False):
        self.currentFile.dedent()
        self.currentFile.writeLine("}" + (";" if semicolon else ""))
