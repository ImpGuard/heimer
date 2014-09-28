from codegen import CodeGenerator
import util

def getPrimitiveParsers():
    primitiveParsers = """
def intParse( s, currentLineNumber ):
\ttry:
\t\treturn int(s)
\texcept ValueError as e:
\t\traise Exception("Parser Error on line %d: Cannot parse %s as int." % ( currentLineNumber, s ))

def boolParse( s, currentLineNumber ):
\ttrueStrings = ["1", "true", "True"]
\tfalseStrings = ["0", "false", "False"]
\tif s in trueStrings:
\t\treturn True
\telif s in falseStrings:
\t\treturn False
\telse:
\t\traise Exception("Parser Error on line %d: Cannot parse %s as bool, it must either be '1', '0', \
    'true', 'True', 'false' or 'False'." % ( currentLineNumber, s ))

def stringParse( s, currentLineNumber ):
\treturn s

def floatParse( s, currentLineNumber ):
\ttry:
\t\treturn float(s)
\texcept ValueError as e:
\t\traise Exception("Parser Error on line %d: Cannot parse %s as float." % ( currentLineNumber, s ))

def intListParse( strings, currentLineNumber ):
\tintList = []
\tfor s in strings:
\t\tintList.append(intParse( s, currentLineNumber ))
\treturn intList

def boolListParse( strings, currentLineNumber ):
\tboolList = []
\tfor s in strings:
\t\tboolList.append(boolParse( s, currentLineNumber ))
\treturn boolList

def stringListParse( strings, currentLineNumber ):
\tstringList = []
\tfor s in strings:
\t\tstringList.append(stringParse( s, currentLineNumber ))
\treturn stringList

def floatListParse( strings, currentLineNumber ):
\tfloatList = []
\tfor s in strings:
\t\tfloatList.append(floatParse( s, currentLineNumber ))
\treturn floatList


"""
    primitiveParsers = primitiveParsers.replace( "intParse", CodeGenerator.PARSE_INT )
    primitiveParsers = primitiveParsers.replace( "boolParse", CodeGenerator.PARSE_BOOL )
    primitiveParsers = primitiveParsers.replace( "stringParse", CodeGenerator.PARSE_STRING )
    primitiveParsers = primitiveParsers.replace( "floatParse", CodeGenerator.PARSE_FLOAT )
    primitiveParsers = primitiveParsers.replace( "intListParse", CodeGenerator.PARSE_INT_LIST )
    primitiveParsers = primitiveParsers.replace( "boolListParse", CodeGenerator.PARSE_BOOL_LIST )
    primitiveParsers = primitiveParsers.replace( "stringListParse", CodeGenerator.PARSE_STRING_LIST )
    primitiveParsers = primitiveParsers.replace( "floatListParse", CodeGenerator.PARSE_FLOAT_LIST )

    # Replace the tabs with the appropriate amount of indent spaces
    primitiveParsers = primitiveParsers.replace( "\t", util.HeimerFile.indentString )

    return primitiveParsers