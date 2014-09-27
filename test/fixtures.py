from javagen import JavaGenerator
import os

class GeneratorFixture:

    filename = "test"

    def __init__( self, generator, mainFileName):
        self.generator = generator

        def insertedMainFunction(self):
            mainFile = open( mainFileName, "r" )
            for line in mainFile:
                self.output.writeLine(line)
            self.output.writeNewLine()

        self.generator.generateMainFunction = insertedMainFunction

    def run():
        self.generator.codegen()


class JavaFixture(GeneratorFixture):

    def __init__( self, mainFileName, formatFileName ):
        parser = HeimerFormatFileParser(formatFileName)
        formatObject = HeimerFormat(parser.objectModel)
        generator = JavaGenerator(GeneratorFixture.filename + ".java", formatObject)
        GeneratorFixture.__init__( self, generator, mainFileName )

class PythonFixture(GeneratorFixture):

    def __init__( self, mainFileName, formatFileName ):
        parser = HeimerFormatFileParser(formatFileName)
        formatObject = HeimerFormat(parser.objectModel)
        generator = PythonGenerator(GeneratorFixture.filename + ".java", formatObject)
        GeneratorFixture.__init__( self, generator, mainFileName )

class CPPFixture(GeneratorFixture):
    def __init__( self, mainFileName, formatFileName ):
        parser = HeimerFormatFileParser(formatFileName)
        formatObject = HeimerFormat(parser.objectModel)
        generator = CPPGenerator(GeneratorFixture.filename + ".cc", formatObject)
        GeneratorFixture.__init__( self, generator, mainFileName )

def createGeneratorFixture(fixtureType, formatFileName):
    # setup temp directory and generate code there
    fixture = fixtureType( dirPath + "Main", formatFileName )
    return fixture()
