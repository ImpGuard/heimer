from codegen import CodeGenerator
from parser import StringConstants
from converter import *

""" Class for generating C++ code. """
class CPPGenerator(CodeGenerator):

    def generateFileHeader(self):
        """ For generating the file header, such as the import statements. """
        pass

    def generateHelperFunctions(self):
        """ Generate any helper functions that will be useful when parsing in the separate util file. """
        pass

    def generateClasses(self):
        """ For generating code segment that defines all the data structures needed by the parser. """
        pass

    def generateOptionVariables(self):
        """ Generate global option variables that will be initialized when parsing. """
        pass

    def generateOptionParserFunction(self):
        """ For generating the function to parse command line options. """
        pass

    def generateInputParserFunction(self):
        """ For generating the function to parse an input file. """
        pass

    def generateRunFunction(self):
        """ For generating the function that will be called by the user. """
        pass

    def generateMain(self):
        """ For generating the empty main method that the user can fill in. """
        pass

    def generateClass( self, className, fieldNamesAndTypes ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The first argument is the class name and the second argument is a dictionary
        containing key-value pairs of the form (field name, field type), both as strings. """
        pass

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
