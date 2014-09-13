""" Base class for generating the parser code. Subclass this for every language supported by Heimer. """
from util import HeimerFile

class CodeGenerator:

    # Filenames
    UTIL_FILE = "HeimerUtil"

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

    def __init__( self, filename, format ):
        self.output = HeimerFile(filename)
        self.format = format
        self.body = format.body()
        self.initialize()

    def initialize(self):
        """ Perform additional initialization if required. """
        pass

    def generateFileHeader(self):
        """ For generating the file header, such as the import statements. """
        raise NotImplementedError()

    def generateHelperFunctions(self):
        """ Generate any helper functions that will be useful when parsing in the separate util file. """
        raise NotImplementedError()

    def generateClasses(self):
        """ For generating code segment that defines all the data structures needed by the parser. """
        for className, fieldNamesAndTypes in self.format.classes():
            self.generateClass( className, fieldNamesAndTypes )

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

    def generateMain(self):
        """ For generating the empty main method that the user can fill in. """
        raise NotImplementedError()

    def generateClass( self, className, fieldNamesAndTypes ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a dictionary
        containing key-value pairs of the form (field name, field type), both as strings. """
        raise NotImplementedError()

    def codeGen(self):
        """ This method is called to generate and write the parser to the specified file. """
        self.generateFileHeader()
        self.generateClasses()
        self.generateOptionVariables()
        self.generateHelperFunctions()
        self.generateOptionParserFunction()
        self.generateInputParserFunction()
        self.generateMain()
        self.output.save()
