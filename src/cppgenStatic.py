from codegen import CodeGenerator
from util import HeimerFile

def cppgenStaticHelpers():
    helpers = """
static const std::string ws = " \\t\\n\\r\\f\\v";

inline std::string rtrim(std::string s, std::string t = ws)
{
\ts.erase(s.find_last_not_of(t) + 1);
\treturn s;
}

inline std::string ltrim(std::string s, std::string t = ws)
{
\ts.erase(0, s.find_first_not_of(t));
\treturn s;
}

inline std::string trim(std::string s, std::string t = ws)
{
\treturn ltrim(rtrim(s, t), t);
}

std::vector<std::string> copyRange(std::vector<std::string> v, int begin, int end)
{
\tusing namespace std;
\tvector<string>::const_iterator first = v.begin() + begin;
\tvector<string>::const_iterator last = v.begin() + end;
\treturn vector<string>(first, last);
}

std::vector<std::string> split(std::string s, std::string delim) {
\tusing namespace std;
\tvector<string> result;

\tsize_t delimLength = delim.length();
\tsize_t start = 0, end = 0;
\twhile ((end = s.find(delim, start)) != string::npos) {
\t\tresult.push_back(s.substr(start, end - start));
\t\tstart = end + delimLength;
\t}
\tresult.push_back(s.substr(start, s.length() - start));

\treturn result;
}

std::string lowercase(std::string &s)
{
\tusing namespace std;
\tchar result[s.length() + 1];
\tfor (unsigned int i = 0; i < s.length(); i++)
\t{
\t\tresult[i] = tolower(s[i]);
\t}
\tresult[s.length()] = NULL;
\treturn string(result);
}

int cppgenParseInt(std::string s, int& lineNumber)
{
\tusing namespace std;
\tstringstream ss(s);
\tint result;
\tss >> result;
\tif (!ss.eof() || ss.fail())
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse \\"" << s << "\\" as int.";
\t\tthrow invalid_argument(err.str());
\t}
\treturn result;
}

bool cppgenParseBool(std::string s, int& lineNumber)
{
\tusing namespace std;
\tif (s.compare("1") == 0 || lowercase(s).compare("true") == 0)
\t{
\t\treturn true;
\t}
\telse if (s.compare("0") == 0 || lowercase(s).compare("false") == 0)
\t{
\t\treturn false;
\t}

\tstringstream err;
\terr << "Parser Error on line " << lineNumber << ": Could not parse \\"" << s << "\\" as bool.";
\tthrow invalid_argument(err.str());
}

std::string cppgenParseString(std::string s, int& lineNumber)
{
\treturn s;
}

float cppgenParseFloat(std::string s, int& lineNumber)
{
\tusing namespace std;
\tstringstream ss(s);
\tfloat result;
\tss >> result;
\tif (!ss.eof() || ss.fail())
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse \\"" << s << "\\" as float.";
\t\tthrow invalid_argument(err.str());
\t}
\treturn result;
}

std::vector<int> cppgenParseIntList(std::vector<std::string> strings, int& lineNumber)
{
\tusing namespace std;
\tif (strings.size() == 0)
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse empty string as list.";
\t\tthrow invalid_argument(err.str());
\t}
\tvector<int> resval;
\tfor (unsigned int i = 0; i < strings.size(); i++)
\t{
\t\tresval.push_back(cppgenParseInt(strings[i], lineNumber));
\t}
\treturn resval;
}

std::vector<bool> cppgenParseBoolList(std::vector<std::string> strings, int& lineNumber)
{
\tusing namespace std;
\tif (strings.size() == 0)
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse empty string as list.";
\t\tthrow invalid_argument(err.str());
\t}
\tvector<bool> resval;
\tfor (unsigned int i = 0; i < strings.size(); i++)
\t{
\t\tresval.push_back(cppgenParseBool(strings[i], lineNumber));
\t}
\treturn resval;
}

std::vector<std::string> cppgenParseStringList(std::vector<std::string> strings, int& lineNumber)
{
\tusing namespace std;
\tif (strings.size() == 0)
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse empty string as list.";
\t\tthrow invalid_argument(err.str());
\t}
\tvector<string> resval;
\tfor (unsigned int i = 0; i < strings.size(); i++)
\t{
\t\tresval.push_back(cppgenParseString(strings[i], lineNumber));
\t}
\treturn resval;
}

std::vector<float> cppgenParseFloatList(std::vector<std::string> strings, int& lineNumber)
{
\tusing namespace std;
\tif (strings.size() == 0)
\t{
\t\tstringstream err;
\t\terr << "Parser Error on line " << lineNumber << ": Could not parse empty string as list.";
\t\tthrow invalid_argument(err.str());
\t}
\tvector<float> resval;
\tfor (unsigned int i = 0; i < strings.size(); i++)
\t{
\t\tresval.push_back(cppgenParseFloat(strings[i], lineNumber));
\t}
\treturn resval;
}

std::string readLine(std::ifstream &f, std::string className)
{
\tusing namespace std;
\tif (f.eof())
\t{
\t\tstringstream err;
\t\terr << "Parser Error: Reached end of file while parsing object \\"" << className << "\\".";
\t\tthrow runtime_error(err.str());
\t}
\tstring result;
\tgetline(f, result);
\tif (f.bad())
\t{
\t\tthrow runtime_error("IO Error: Unknown problem when reading input file.");
\t}
\treturn result;
}

void seek(std::ifstream &f, std::streampos pos)
{
\tusing namespace std;
\tf.seekg(pos);
\tif (f.bad())
\t{
\t\tthrow runtime_error("IO Error: Unknown problem when reading input file.");
\t}
}

std::streampos getFilePointer(std::ifstream &f)
{
\tusing namespace std;
\tstreampos pos = f.tellg();
\tif (pos == -1)
\t{
\t\tthrow runtime_error("IO Error: Unknown problem when reading input file.");
\t}
\treturn pos;
}
"""

    helpers = helpers.replace("cppgenParseIntList", CodeGenerator.PARSE_INT_LIST)
    helpers = helpers.replace("cppgenParseBoolList", CodeGenerator.PARSE_BOOL_LIST)
    helpers = helpers.replace("cppgenParseStringList", CodeGenerator.PARSE_STRING_LIST)
    helpers = helpers.replace("cppgenParseFloatList", CodeGenerator.PARSE_FLOAT_LIST)
    helpers = helpers.replace("cppgenParseInt", CodeGenerator.PARSE_INT)
    helpers = helpers.replace("cppgenParseBool", CodeGenerator.PARSE_BOOL)
    helpers = helpers.replace("cppgenParseString", CodeGenerator.PARSE_STRING)
    helpers = helpers.replace("cppgenParseFloat", CodeGenerator.PARSE_FLOAT)

    # Replace the tabs with the appropriate amount of indent spaces
    helpers = helpers.replace( "    ", HeimerFile.indentString )

    return helpers
