from parser import HeimerFormatFileParser
from converter import HeimerFormat
from pygen import PythonGenerator
from javagen import JavaGenerator
from cppgen import CPPGenerator

from sys import exit
from optparse import OptionParser

USAGE = "usage: %prog [options] format_file_name"
DEFAULT_LANGUAGE = "python"

if __name__ == "__main__":
    # Option parser
    optParser = OptionParser(usage = USAGE)
    optParser.add_option( "-l", "--lang", action = "store", dest = "language",
            help = "specifies the output parser language. Defaults to using the extension on the output file name or Python. \n"
                   "Accepts 'python', 'java', or 'c++'." )
    optParser.add_option( "-o", "--output", action = "store", dest = "outputName", default = "out",
            help = "specifies the output file name" )
    (options, args) = optParser.parse_args()

    # Clean up provided flags
    if options.language == None:
        periodIndex = options.outputName.find(".")
        if periodIndex == -1:
            options.language = DEFAULT_LANGUAGE
        else:
            extension = options.outputName[options.outputName.find(".") + 1:]
            if extension == "py":
                options.language = "python"
            elif extension == "java":
                options.language = "java"
            elif extension in [ "c", "cc", "cpp" ]:
                options.language = "c++"

    # Check that a format file is provided
    if len(args) != 1:
        optParser.print_help()
        exit(1)

    # Parser format file into a object model
    parser = HeimerFormatFileParser(args[0])
    if parser.parseFailed():
        parser.printFailures()
        exit(1)

    # Generate a format object from the object model
    formatObject = HeimerFormat(parser.objectModel)

    # Depending on output language, call the associated code generator
    generator = None
    if options.language == "python":
        generator = PythonGenerator(options.outputName, formatObject)
    elif options.language == "java":
        generator = JavaGenerator(options.outputName, formatObject)
    elif options.language == "c++":
        generator = CPPGenerator(options.outputName, formatObject)
    else:
        print "language not supported."
        exit(1)

    generator.codeGen()
