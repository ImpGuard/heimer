from codegen import CodeGenerator
from util import HeimerFile

def pygenStaticHelpers():
    helpers = """
def readline(inputFile):
\tline = inputFile.readline()
\tif line == "":
\t\traise EOFError()
\treturn line.strip()

def intParse( s, currentLineNumber ):
\ttry:
\t\treturn int(s)
\texcept ValueError as e:
\t\traise ValueError("Parser Error on line %d: Cannot parse '%s' as int." % ( currentLineNumber, s ))

def boolParse( s, currentLineNumber ):
\ttrueStrings = ["1", "true", "True"]
\tfalseStrings = ["0", "false", "False"]
\tif s in trueStrings:
\t\treturn True
\telif s in falseStrings:
\t\treturn False
\telse:
\t\traise ValueError("Parser Error on line %d: Cannot parse '%s' as bool, it must either be '1', '0', \
    'true', 'True', 'false' or 'False'." % ( currentLineNumber, s ))

def stringParse( s, currentLineNumber ):
\treturn s

def floatParse( s, currentLineNumber ):
\ttry:
\t\treturn float(s)
\texcept ValueError as e:
\t\traise ValueError("Parser Error on line %d: Cannot parse '%s' as float." % ( currentLineNumber, s ))

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
    helpers = helpers.replace( "\t", HeimerFile.indentString )

    return helpers
