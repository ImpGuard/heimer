from codegen import CodeGenerator
from util import HeimerFile

def javagenStaticHelpers():
    helpers = """
public static int javagenParseInt(String s, int[] lineNumber)
{
\ttry
\t{
\t\treturn Integer.parseInt(s);
\t}
\tcatch (NumberFormatException e)
\t{
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse \" + s + \" as int\");
\t}
}

public static boolean javagenParseBool(String s, int[] lineNumber)
{
\tif (s.equals("1") || s.toLowerCase().equals("true"))
\t{
\t\treturn true;
\t}
\telse if (s.equals("0") || s.toLowerCase().equals("false"))
\t{
\t\treturn false;
\t}
\tthrow new NumberFormatException(
\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse \" + s + \" as bool\");
}

public static String javagenParseString(String s, int[] lineNumber)
{
\treturn s;
}

public static float parseFloat(String s, int[] lineNumber)
{
\ttry
\t{
\t\treturn Float.parseFloat(s);
\t}
\tcatch (NumberFormatException e)
\t{
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse \" + s + \" as float\");
\t}
}

public static ArrayList<Integer> javagenParseIntList(String[] strings, int[] lineNumber)
{
\tif (strings.length == 0)
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse empty string as list\");
\tArrayList<Integer> resval = new ArrayList<Integer>();
\tfor (String s : strings)
\t\tresval.add(javagenParseInt(s, lineNumber));
\treturn resval;
}

public static ArrayList<Boolean> javagenParseBoolList(String[] strings, int[] lineNumber)
{
\tif (strings.length == 0)
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse empty string as list\");
\tArrayList<Boolean> resval = new ArrayList<Boolean>();
\tfor (String s : strings)
\t\tresval.add(javagenParseBool(s, lineNumber));
\treturn resval;
}

public static ArrayList<String> javagenParseStringList(String[] strings, int[] lineNumber)
{
\tif (strings.length == 0)
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse empty string as list\");
\tArrayList<String> resval = new ArrayList<String>();
\tfor (String s : strings)
\t\tresval.add(javagenParseString(s, lineNumber));
\treturn resval;
}

public static ArrayList<Float> javagenParseFloatList(String[] strings, int[] lineNumber)
{
\tif (strings.length == 0)
\t\tthrow new NumberFormatException(
\t\t\t\"Parser Error on line \" + lineNumber[0] + \": Could not parse empty string as list\");
\tArrayList<Float> resval = new ArrayList<Float>();
\tfor (String s : strings)
\t\tresval.add(javagenParseFloat(s, lineNumber));
\treturn resval;
}

public static String readLine(RandomAccessFile f)
{
\ttry
\t{
\t\tString result = f.readLine();
\t\tif (result == null) throw new EOFException();
\t\treturn result;
\t}
\tcatch (IOException e)
\t{
\t\tthrow new RuntimeException("IO Error: Unknown problem when reading input file");
\t}
}

public static void seek(RandomAccessFile f, long pos)
{
\ttry
\t{
\t\tf.seek(pos);
\t}
\tcatch (IOException e)
\t{
\t\tthrow new RuntimeException("IO Error: Unknown problem when reading input file");
\t}
}

public static long getFilePointer(RandomAccessFile f)
{
\ttry
\t{
\t\treturn f.getFilePointer();
\t}
\tcatch (IOException e)
\t{
\t\tthrow new RuntimeException("IO Error: Unknown problem when reading input file");
\t}
}
"""

    helpers = helpers.replace("javagenParseInt", CodeGenerator.PARSE_INT)
    helpers = helpers.replace("javagenParseBool", CodeGenerator.PARSE_BOOL)
    helpers = helpers.replace("javagenParseString", CodeGenerator.PARSE_STRING)
    helpers = helpers.replace("javagenParseFloat", CodeGenerator.PARSE_FLOAT)
    helpers = helpers.replace("javagenParseIntList", CodeGenerator.PARSE_INT_LIST)
    helpers = helpers.replace("javagenParseBoolList", CodeGenerator.PARSE_BOOL_LIST)
    helpers = helpers.replace("javagenParseStringList", CodeGenerator.PARSE_STRING_LIST)
    helpers = helpers.replace("javagenParseFloatList", CodeGenerator.PARSE_FLOAT_LIST)

    # Replace the tabs with the appropriate amount of indent spaces
    helpers = helpers.replace( "\t", HeimerFile.indentString )

    return helpers
