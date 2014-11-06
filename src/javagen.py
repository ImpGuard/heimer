from codegen import CodeGenerator
from javagenStatic import *
from util import *

from optparse import OptionParser
from os.path import join, splitext, basename

""" Class for generating Java code. """
class JavaGenerator(CodeGenerator):

    def initialize(self):
        """ Perform additional initialization if required. """
        self.main.setExtension("java")
        self.util.setExtension("java")
        self.classFiles = []

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateClasses()
        self.generateUtilFile()
        self.generateMainFile()
        self.main.save()
        self.util.save()
        map(lambda c: c.save(), self.classFiles)

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of
        fields (in order) of that class. """
        self.typeNameToParseFuncName[className] = "parse%s" % className
        classFile = HeimerFile(join(self.foldername, className + ".java"))
        self.classFiles.append(classFile)
        self.currentFile = classFile

        shouldImportArrayList = False

        self._beginBlock("public class " + className )

        for field in fields:
            if field.isRepeating() or field.isList():
                shouldImportArrayList = True
            classFile.writeLine("public " + self._getTypeName(field) + " " + field.name() + ";")

        if shouldImportArrayList:
            classFile.writeImportLine("")
            classFile.writeImportLine("import java.util.ArrayList;")

        self._endBlock()

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFile(self):
        self.currentFile = self.util
        self.generateUtilFileHeader()
        self._beginBlock("public class " + CodeGenerator.UTIL_FILE_NAME)
        self.generateHelperFunctions()
        self.generateClassParserFunctions()
        self._endBlock()

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        # Import library headers
        self.currentFile.writeLine("import java.util.ArrayList;")
        self.currentFile.writeLine("import java.util.Arrays;")
        self.currentFile.writeLine("import java.io.RandomAccessFile;")
        self.currentFile.writeLine("import java.io.EOFException;")
        self.currentFile.writeLine("import java.io.IOException;")

        self.currentFile.writeNewline()

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        # Static helpers for primitives
        helpers = javagenStaticHelpers()
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
            # Helper to do some setup in every parser function
            writeLine(className + " result = new " + className + "();")
            didSplit = False
            didRepeat = False
            didRepeatPlus = False

            for line in lines:
                didRepeat = didRepeat or line.isRepeating()
                didRepeatPlus = didRepeatPlus or  line.isOneOrMoreRepetition()
                didSplit = didSplit or line.numFields() > 1 or (not line.isEmpty() and line.getField(0).isList())

            if didSplit:
                writeLine("String[] fields;")
            if didRepeat:
                writeLine("long prevFilePos = getFilePointer(f);")
                writeLine("int prevLineNumber = lineNumber[0];")
            if didRepeatPlus:
                writeLine("boolean didRepeatOnce = false;")

        def handleEmptyLine():
            # Handle the empty line case
            self._beginBlock("if (!readLine(f).trim().equals(\"\"))")
            writeLine("throw new RuntimeException(\"Parser Error on line \" + lineNumber[0] +" +
                "\": Should be an empty line\");")
            self._endBlock()
            writeLine("lineNumber[0] += 1;")

        def handleSimpleLineOneField(field):
            # Helper for handleSimpleLine
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f), lineNumber);")
                writeLine("lineNumber[0] += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = readLine(f).split(\"" + self.format.lineDelimiter() + "\");")
                write("result." + field.name() + " = "
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()] + "(fields, lineNumber);")
                writeLine("lineNumber[0] += 1;")
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
                writeLine("result." + field.name() + " = "
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()]
                    + "(Arrays.copyOfRange(fields, " + str(index) + ", fields.length), lineNumber);")
            else:
                # Field is a class? Cannot be!
                raise Exception("This should never happen.")

            writeLine("lineNumber[0] += 1;")

        def handleSimpleLine(line):
            if line.numFields() == 1:
                # Only one field, no need to split unnecessarily
                handleSimpleLineOneField(line.getField(0))
            else:
                # Multiple fields, split it
                writeLine("fields = readLine(f).split(\"" + self.format.lineDelimiter() + "\");")
                if (line.getField(-1).isList()):
                    self._beginBlock("if (fields.length < " + str(line.numFields()) + ")")
                else:
                    self._beginBlock("if (fields.length != " + str(line.numFields()) + ")")
                writeLine("throw new RuntimeException(\"Parser Error on line \" + lineNumber[0] + " +
                    "\": Expecting " + str(line.numFields()) + " fields (\" + fields.length + \" found)\");")
                self._endBlock()
                for index, field in enumerate(line):
                    handleSimpleLineMultipleField(index, field)

        def handleRepeatingLineForField(field):
            # Helper for handleRepeating
            if isSimplePrimitive(field):
                # Field is simple, just parse it
                writeLine("result." + field.name() + ".add("
                    + self.typeNameToParseFuncName[field.typeName()] + "(readLine(f), lineNumber));")
                writeLine("lineNumber[0] += 1;")
            elif field.isPrimitive():
                # Field is primitive list, split line
                writeLine("fields = readLine(f).split(\"" + self.format.lineDelimiter() + "\");")
                writeLine("result." + field.name() + ".add("
                    + self.typeNameToParseFuncName["list(%s)" % field.listType()] + "(fields, lineNumber));")
                writeLine("lineNumber[0] += 1;")
            else:
                # Field is a class, recurse
                writeLine("result." + field.name() + ".add("
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
                # Initialize the arraylist
                writeLine("result." + field.name() + " = new " + self._getTypeName(field) + "();")
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
                # Initialize object
                writeLine("result." + field.name() + " = new " + self._getTypeName(field) + "();")
                # Save initial position
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber[0];")
                # Begin infinite loop
                self._beginBlock("while (true)")
                # Main handler
                handleRepeatingLineForField(field)
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber[0];")
                # Check for newline
                if (line.isSplitByNewline()):
                    handleEmptyLine()
                # End infinite loop and try block
                self._endBlock()
                self._endBlock()
                # Catch any errors, reset line number and continue
                self._beginBlock("catch (Exception e)")
                writeLine("seek(f, prevFilePos);")
                writeLine("lineNumber[0] = prevLineNumber;")
                self._endBlock()
            elif line.isOneOrMoreRepetition:
                field = line.getField(0)
                # Wrap with try block
                self._beginBlock("try")
                # Initialize object and checker to ensure at least one repetition
                writeLine("didRepeatOnce = false;")
                writeLine("result." + field.name() + " = new " + self._getTypeName(field) + "();")
                # Begin infinite loop
                self._beginBlock("while (true)")
                # Main handler
                handleRepeatingLineForField(field)
                writeLine("prevFilePos = getFilePointer(f);")
                writeLine("prevLineNumber = lineNumber[0];")
                writeLine("didRepeatOnce = true;")
                # Check for newline
                if (line.isSplitByNewline()):
                    handleEmptyLine()
                # End infinite loop and try block
                self._endBlock()
                self._endBlock()
                # Catch any errors, either (1) reset line number and continue (2) error if did not repeat once
                self._beginBlock("catch (Exception e)")
                self._beginBlock("if (!didRepeatOnce)")
                writeLine("throw new RuntimeException(\"Parser Error on line \" + lineNumber[0] +" +
                    "\": Expecting at least 1 " + field.typeName() + " (0 found)\");")
                self._endBlock()
                writeLine("seek(f, prevFilePos);")
                writeLine("lineNumber[0] = prevLineNumber;")
                self._endBlock()
            else:
                raise Exception("This should never happen.")


        self._beginBlock("public static " + className + " parse" + className + "(RandomAccessFile f, int[] lineNumber)")
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
        self._beginBlock("public class " + splitext(basename(self.currentFile.filename))[0])
        self.generateHelpMessage()
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
        self.currentFile.writeLine("import java.io.RandomAccessFile;")
        self.currentFile.writeLine("import java.io.FileNotFoundException;")
        self.currentFile.writeLine("import java.io.IOException;")
        self.currentFile.writeLine("import java.io.EOFException;")
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
        self.currentFile.write("public static String USAGE = \"" + helpMessage[0] + "\\n\"")
        for index, helpString in enumerate(helpMessage[1:]):
            self.currentFile.writeNewline()
            if index == 0:
                self.currentFile.indent()
            self.currentFile.write(" + \"" + helpString + "\\n\"")
        self.currentFile.writeLine(";")

        if len(helpMessage) > 1:
            self.currentFile.dedent()

        self.currentFile.writeNewline()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        self._beginBlock("public static void main(String[] args)")
        self.currentFile.writeLine(self.bodyTypeName + " " + CodeGenerator.PARSED_OBJ + " = "
            + CodeGenerator.RUN + "(args);")
        self._endBlock()
        self.currentFile.writeNewline()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        if len(self.format.commandLineOptions()) == 0:
            # Just handle extraneous inputs
            self._beginBlock("private static void " + CodeGenerator.PARSE_OPTIONS + "(String[] args)")
            self._beginBlock("for ( int i = 0; i < args.length; i++ )")
            self.currentFile.writeLine(CodeGenerator.USER_ARGS + ".add(args[i]);")
            self._endBlock()
            self._endBlock()
            return

        writeLine = self.currentFile.writeLine
        options = self.format.commandLineOptions()

        # Create helper for code generation
        def handleOption( option, typeOfIf ):
            self._beginBlock(typeOfIf + " (args[i].equals(\"-" + option.flagName + "\"))")
            if isBool(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_BOOL + "(args[i + 1], fakeLineNumber);")
            elif isInteger(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_INT + "(args[i + 1], fakeLineNumber);")
            elif isFloat(option.optionType):
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_FLOAT + "(args[i + 1], fakeLineNumber);")
            else:
                writeLine(option.variableName + " = " + CodeGenerator.UTIL_FILE_NAME + "." + CodeGenerator.PARSE_STRING + "(args[i + 1], fakeLineNumber);")
            writeLine("i += 1;")
            self._endBlock()

        # Create option parser function
        self._beginBlock("private static void " + CodeGenerator.PARSE_OPTIONS + "(String[] args)")
        self._beginBlock("try")
        writeLine("int[] fakeLineNumber = {-1};")
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
        self.main.writeLine("System.err.println(USAGE);")
        self.main.writeLine("System.exit(1);")
        self._endBlock()

        # generate code for returning the filename
        self._beginBlock("if (" + CodeGenerator.USER_ARGS + ".size() == 0)")
        writeLine("System.err.println(USAGE);")
        writeLine("System.exit(1);")
        self._endBlock()

        # End of function
        self._endBlock()
        self.currentFile.writeNewline()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        writeLine = self.currentFile.writeLine
        # Begin function declaration
        self._beginBlock("private static " + self.bodyTypeName
            + " " + CodeGenerator.PARSE_INPUT + "(RandomAccessFile f)")

        # Setup line number
        writeLine("int[] lineNumber = {0};")

        # Main try block
        self._beginBlock("try")
        writeLine(self.bodyTypeName + " result = "
            + CodeGenerator.UTIL_FILE_NAME + ".parse" + self.bodyTypeName + "(f, lineNumber);")
        writeLine("String line;")
        self._beginBlock("while ((line = f.readLine()) != null)")
        self._beginBlock("if (!line.equals(\"\"))")
        writeLine("throw new RuntimeException(\"Parser Error: Did not reach end of file\");")
        self._endBlock()
        self._endBlock()
        writeLine("return result;")
        self._endBlock()

        # Begin catch end of file
        self._beginBlock("catch (EOFException e)")
        writeLine("System.err.println(\"Parser Error: Reached end of file before finished parsing\");")
        writeLine("System.exit(1);")
        self._endBlock()

        # Begin other exception catches
        self._beginBlock("catch (Exception e)")
        writeLine("System.err.println(e.getMessage());")
        writeLine("System.exit(1);")
        self._endBlock()

        writeLine("return null;")

        # End function declaration
        self._endBlock()

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        writeLine = self.currentFile.writeLine

        self._beginBlock("public static " + self.bodyTypeName + " "
            + CodeGenerator.RUN + "(String[] args)")

        # Parse Options
        self.currentFile.writeLine(CodeGenerator.PARSE_OPTIONS + "(args);")

        # Parse input file if it exists
        self._beginBlock("if (" + CodeGenerator.USER_ARGS + ".size() != 0)")
        writeLine("String filename = " + CodeGenerator.USER_ARGS + ".get(0);")
        # Try to parse the file
        self._beginBlock("try")
        writeLine("RandomAccessFile f = new RandomAccessFile(filename, \"r\");")
        writeLine(self.bodyTypeName + " result = " + CodeGenerator.PARSE_INPUT + "(f);")
        writeLine("f.close();")
        writeLine("return result;")
        self._endBlock()
        # File not found!
        self._beginBlock("catch (FileNotFoundException e)")
        writeLine("System.err.println(\"Input file '\" + filename + \"' not found\");")
        writeLine("System.exit(1);")
        self._endBlock()
        self._beginBlock("catch (IOException e)")
        writeLine("System.err.println(\"Could not open '\" + filename + \"'\");")
        self._endBlock()
        self._endBlock()
        # Otherwise error
        self._beginBlock("else")
        writeLine("System.err.println(USAGE);");
        writeLine("System.exit(1);")
        self._endBlock()

        writeLine("return null;")

        self._endBlock()
        self.currentFile.writeNewline()

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
            return "ArrayList<" + self._getBasicTypeName(listType(typeName)) + ">"
        else:
            return None


    def _getTypeName( self, field ):
        typeName = self._getBasicTypeName(field.typeName())
        if typeName == None:
            typeName = field.typeName()

        if field.isRepeating():
            return "ArrayList<" + typeName + ">"
        else:
            return typeName

    def _beginBlock( self, line ):
        self.currentFile.writeLine(line)
        self.currentFile.writeLine("{")
        self.currentFile.indent()

    def _endBlock(self):
        self.currentFile.dedent()
        self.currentFile.writeLine("}")
