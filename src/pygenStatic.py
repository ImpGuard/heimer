from codegen import CodeGenerator
from util import InstaParseFile

def pygenStaticHelpers():
    helpers = """
def readline(inputFile, className):
\tline = inputFile.readline()
\tif line == "":
\t\traise ValueError("Parser Error: Reached end of file while parsing object \\"" + className + "\\".")
\treturn line.strip()

def intParse( s, currentLineNumber ):
\ttry:
\t\treturn int(s)
\texcept ValueError as e:
\t\traise ValueError("Parser Error on line %d: Could not parse \\\"%s\\\" as int." % ( currentLineNumber, s ))

def boolParse( s, currentLineNumber ):
\tif s == "1" or s.lower() == "true":
\t\treturn True
\telif s == "0" or s.lower() == "false":
\t\treturn False
\traise ValueError("Parser Error on line %d: Could not parse \\\"%s\\\" as bool." % ( currentLineNumber, s ))

def stringParse( s, currentLineNumber ):
\treturn s

def floatParse( s, currentLineNumber ):
\ttry:
\t\treturn float(s)
\texcept ValueError as e:
\t\traise ValueError("Parser Error on line %d: Could not parse \\\"%s\\\" as float." % ( currentLineNumber, s ))

def intListParse( strings, currentLineNumber ):
\tintList = []
\tif len(strings) == 0:
\t\traise ValueError("Parser Error on line %d: Could not parse empty string as list." % currentLineNumber)
\tfor s in strings:
\t\tintList.append(intParse( s, currentLineNumber ))
\treturn intList

def boolListParse( strings, currentLineNumber ):
\tboolList = []
\tif len(strings) == 0:
\t\traise ValueError("Parser Error on line %d: Could not parse empty string as list." % currentLineNumber)
\tfor s in strings:
\t\tboolList.append(boolParse( s, currentLineNumber ))
\treturn boolList

def stringListParse( strings, currentLineNumber ):
\tstringList = []
\tif len(strings) == 0:
\t\traise ValueError("Parser Error on line %d: Could not parse empty string as list." % currentLineNumber)
\tfor s in strings:
\t\tstringList.append(stringParse( s, currentLineNumber ))
\treturn stringList

def floatListParse( strings, currentLineNumber ):
\tfloatList = []
\tif len(strings) == 0:
\t\traise ValueError("Parser Error on line %d: Could not parse empty string as list." % currentLineNumber)
\tfor s in strings:
\t\tfloatList.append(floatParse( s, currentLineNumber ))
\treturn floatList


"""
    helpers = helpers.replace( "intParse", CodeGenerator.PARSE_INT )
    helpers = helpers.replace( "boolParse", CodeGenerator.PARSE_BOOL )
    helpers = helpers.replace( "stringParse", CodeGenerator.PARSE_STRING )
    helpers = helpers.replace( "floatParse", CodeGenerator.PARSE_FLOAT )
    helpers = helpers.replace( "intListParse", CodeGenerator.PARSE_INT_LIST )
    helpers = helpers.replace( "boolListParse", CodeGenerator.PARSE_BOOL_LIST )
    helpers = helpers.replace( "stringListParse", CodeGenerator.PARSE_STRING_LIST )
    helpers = helpers.replace( "floatListParse", CodeGenerator.PARSE_FLOAT_LIST )

    # Replace the tabs with the appropriate amount of indent spaces
    helpers = helpers.replace( "\t", InstaParseFile.indentString )

    return helpers
