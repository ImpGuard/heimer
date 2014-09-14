""" Base class for generating the parser code. Subclass this for every language supported by Heimer. """
from util import HeimerFile

class CodeGenerator:

    # Filenames
    UTIL_FILE_NAME = "HeimerUtil"
    DATA_FILE_NAME = "HeimerData"

    # Used variable names
    USER_ARGS = "userArgs"

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
    PARSE_OPTIONS = "parseOptions"
    PARSE_INPUT = "parseInput"
    RUN = "run"

    def __init__( self, filename, format ):
        self.output = HeimerFile(filename)
        self.util = HeimerFile(CodeGenerator.UTIL_FILE_NAME)
        self.data = HeimerFile(CodeGenerator.DATA_FILE_NAME)
        self.format = format
        self.classes = format.classes()
        self.body = format.body()
        self.currentFile = None
        self.initialize()

    def initialize(self):
        """ Perform additional initialization if required. """
        pass

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateDataFile()
        self.generateUtilFile()
        self.generateMainFile()
        self.output.save()
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
        for className, fieldNamesAndTypes in self.format.classFormats():
            self.generateClass( className, fieldNamesAndTypes )

    def generateClass( self, className, fieldNamesAndTypes ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a dictionary
        containing key-value pairs of the form (field name, field type), both as strings. """
        raise NotImplementedError()

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
        raise NotImplementedError()

    def generateHelperFunctions(self):
        """ For generating the helper functions that will be useful when parsing in the util file. """
        raise NotImplementedError()

    ################################################################################
    # Generate Main File
    ################################################################################

    def generateMainFile(self):
        """ Generate main file where the main function resides. """
        self.currentFile = self.output
        self.generateMainFileHeader()
        self.generateOptionVariables()
        self.generateOptionParserFunction()
        self.generateInputParserFunction()
        self.generateRunFunction()
        self.generateMainFunction()

    def generateMainFileHeader(self):
        """ For generating the main file header, such as the import statements. """
        raise NotImplementedError()

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        raise NotImplementedError()

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        raise NotImplementedError()

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        raise NotImplementedError()

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        raise NotImplementedError()

    def generateMainFunction(self):
        """ For generating the empty main method that the user can fill in. """
        raise NotImplementedError()
