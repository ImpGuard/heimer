from codegen import CodeGenerator

def staticHelpers():
    helpers = """
public static int javagenParseInt(String s)
{
\treturn Integer.parseInt(s);
}

public static boolean javagenParseBool(String s)
{
\tif (s.equals("1") || s.toLowerCase().equals("true"))
\t{
\t\treturn true;
\t}
\telse if (s.equals("0") || s.toLowerCase().equals("false"))
\t{
\t\treturn false;
\t}
\tthrow new NumberFormatException();
}

public static String javagenParseString(String s)  {
\treturn s;
}

public static float parseFloat(String s) {
\treturn Float.parseFloat(s);
}

public static ArrayList<Integer> javagenParseIntList(String[] strings)
{
\tArrayList<Integer> resval = new ArrayList<Integer>();
\tfor (String s : strings)
\t{
\t\tresval.add(javagenParseInt(s));
\t}
\treturn resval;
}

public static ArrayList<Boolean> javagenParseBoolList(String[] strings)
{
\tArrayList<Boolean> resval = new ArrayList<Boolean>();
\tfor (String s : strings)
\t{
\t\tresval.add(javagenParseBool(s));
\t}
\treturn resval;
}

public static ArrayList<String> javagenParseStringList(String[] strings)
{
\tArrayList<String> resval = new ArrayList<String>();
\tfor (String s : strings)
\t{
\t\tresval.add(javagenParseString(s));
\t}
\treturn resval;
}

public static ArrayList<Float> javagenParseFloatList(String[] strings)
{
\tArrayList<Float> resval = new ArrayList<Float>();
\tfor (String s : strings)
\t{
\t\tresval.add(javagenParseFloat(s));
\t}
\treturn resval;
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

    return helpers
