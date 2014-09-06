""" Base class for generating the parser code. Subclass this for every language supported by Heimer. """
from utils import HeimerFile

class CodeGenerator:

    def __init__( self, format ):
        self.format = format
        self.body = format.body()

    def generateFileHeader( self, outputFile ):
        """ For generating the file header, such as the import statements. """
        raise NotImplementedError()

    def generateClasses( self, outputFile ):
        """ For generating code segment that defines all the data structures needed by the parser. """
        for className, fieldNamesAndTypes in self._format.classes():
            generateClass( outputFile, className, fieldNamesAndTypes )

    def generateOptionParserFunction( self, outputFile ):
        """ For generating the function to parse command line options. """
        raise NotImplementedError()

    def generateInputParserFunction( self, outputFile ):
        """ For generating the function to parse an input file. """
        raise NotImplementedError()

    def generateRunFunction( self, outputFile ):
        """ For generating the function that will be called by the user. """
        raise NotImplementedError()

    def generateMain( self, outputFile ):
        """ For generating the empty main method that the user can fill in. """
        raise NotImplementedError()

    def generateClass( self, outputFile, className, fieldNamesAndTypes ):
        """ Helper function for generating the code segement defining a class (or the corresponding
        data structure). The second argument is the class name and the third argument is a dictionary
        containing key-value pairs of the form (field name, field type), both as strings. """
        raise NotImplementedError()

    def codeGen( self, filename ):
        """ This method is called to generate and write the parser to the specified file. """
        outputFile = HeimerFile(filename)
        self.generateFileHeader(outputFile)
        self.generateClasses(outputFile)
        self.generateOptionParserFunction(outputFile)
        self.generateInputParserFunction(outputFile)
        self.generateMain(outputFile)
        outputFile.save()

