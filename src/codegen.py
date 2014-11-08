from util import HeimerFile, StringConstants
from os.path import dirname, basename, join

class CodeGenerator:
    """ Base class for generating the parser code. Subclass this for every language supported by Heimer. """

    # Namespace
    PARSER_NAME = "Heimer"

    # Filenames
    UTIL_FILE_NAME = PARSER_NAME + "Util"
    DATA_FILE_NAME = PARSER_NAME + "Data"

    # Used variable names
    USER_ARGS = "userArgs"
    PARSED_OBJ = "parsedObject"

    # Method/Function names
    PARSE_INT = "parseInt"
    PARSE_BOOL = "parseBool"
    PARSE_STRING = "parseString"
    PARSE_FLOAT = "parseFloat"
    PARSE_INT_LIST = "parseIntList"
    PARSE_BOOL_LIST = "parseBoolList"
    PARSE_STRING_LIST = "parseStringList"
    PARSE_FLOAT_LIST = "parseFloatList"
    PARSE_NEWLINE = "parseNewline"
    PARSE_INPUT = "parse"

    def __init__( self, filename, format ):
        self.foldername = dirname(filename)
        self.filename = basename(filename)
        self.main = HeimerFile(filename)
        self.util = HeimerFile(join(self.foldername, CodeGenerator.UTIL_FILE_NAME))
        self.data = HeimerFile(join(self.foldername, CodeGenerator.DATA_FILE_NAME))
        self.format = format
        self.classes = format.classes()
        self.bodyTypeName = format.bodyTypeName()
        self.currentFile = None
        self.typeNameToParseFuncName = {
            StringConstants.INTEGER_TYPE: CodeGenerator.PARSE_INT,
            StringConstants.FLOAT_TYPE: CodeGenerator.PARSE_FLOAT,
            StringConstants.STRING_TYPE: CodeGenerator.PARSE_STRING,
            StringConstants.BOOL_TYPE: CodeGenerator.PARSE_BOOL,
            "list(%s)" % StringConstants.INTEGER_TYPE: CodeGenerator.PARSE_INT_LIST,
            "list(%s)" % StringConstants.FLOAT_TYPE: CodeGenerator.PARSE_FLOAT_LIST,
            "list(%s)" % StringConstants.STRING_TYPE: CodeGenerator.PARSE_STRING_LIST,
            "list(%s)" % StringConstants.BOOL_TYPE: CodeGenerator.PARSE_BOOL_LIST,
        }
        self.initialize()

    def initialize(self):
        """ Perform additional initialization if required. """
        pass

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateDataFile()
        self.generateUtilFile()
        self.generateMainFile()
        self.main.save()
        self.util.save()
        self.data.save()

    ################################################################################
    # Generate Data File
    ################################################################################

    def generateDataFile(self):
        """ Generate classes in a separate data file. """
        self.currentFile = self.data
        self.generateDataFileHeader()
        self.generateClasses()

    def generateDataFileHeader(self):
        """ For generating the data file header, such as the import statements. """
        raise NotImplementedError()

    def generateClasses(self):
        """ For generating code segment that defines all the data structures needed by the parser. """
        for className, lines in self.classes.items():
            fields = []
            for line in lines:
                for field in line:
                    fields.append(field)
            self.generateClass( className, fields )
            #The name for the parseing function for class X is parseX
            self.typeNameToParseFuncName[className] = "parse%s" % className

    def generateClass( self, className, fields ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a list of
        fields (in order) of that class. """
        print "classGen"
        raise NotImplementedError()

    ################################################################################
    # Generate Util File
    ################################################################################

    def generateUtilFile(self):
        """ Generate helper functions in the separate util file. """
        self.currentFile = self.util
        self.generateUtilFileHeader()
        self.generateHelperFunctions()
        self.generateClassParserFunctions()

    def generateUtilFileHeader(self):
        """ For generating the util file header, such as the import statements. """
        raise NotImplementedError()

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        raise NotImplementedError()

    def generateClassParserFunctions(self):
        """ For generating all the functions for parsing user defined classes. """
        for className, lines in self.classes.items():
            self.generateClassParserFunction( className, lines )

    def generateClassParserFunction( self, className, lines ):
        """ For generating a helper functions for parsing a user defined class. The first argument
        is the class name and the second argument is a list of FormatLine's. """
        raise NotImplementedError

    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFile(self):
        """ Generate main file where the main function resides. """
        self.currentFile = self.main
        self.generateMainFileHeader()
        self.generateInputParserFunction()
        self.generateMainFunction()

    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        raise NotImplementedError()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        raise NotImplementedError()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        raise NotImplementedError()
