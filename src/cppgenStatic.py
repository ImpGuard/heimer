from codegen import CodeGenerator
from util import HeimerFile

def cppgenStaticHelpers():
    helpers = """
static const std::string ws = " \\t\\n\\r\\f\\v";

inline std::string rtrim(std::string s, std::string t = ws)
{
    s.erase(s.find_last_not_of(t) + 1);
    return s;
}

inline std::string ltrim(std::string s, std::string t = ws)
{
    s.erase(0, s.find_first_not_of(t));
    return s;
}

inline std::string trim(std::string s, std::string t = ws)
{
    return ltrim(rtrim(s, t), t);
}

std::vector<std::string> copyRange(std::vector<std::string> v, int begin, int length)
{
    using namespace std;
    vector<string>::const_iterator first = v.begin() + begin;
    vector<string>::const_iterator last = v.begin() + begin + length;
    return vector<string>(first, last);
}

std::vector<std::string> split(std::string s, std::string delim) {
    using namespace std;
    vector<string> result;

    size_t delimLength = delim.length();
    size_t start = 0, end = 0;
    while ((end = s.find(delim, start)) != string::npos) {
        result.push_back(s.substr(start, end - start));
        start = end + delimLength;
    }
    result.push_back(s.substr(start, s.length() - start));

    return result;
}

std::string lowercase(std::string &s)
{
    using namespace std;
    char result[s.length()];
    for (unsigned int i = 0; i < s.length(); i++)
    {
        result[i] = tolower(s[i]);
    }
    return string(result);
}

int cppgenParseInt(std::string s, int& lineNumber)
{
    using namespace std;
    stringstream ss(s);
    int result;
    ss >> result;
    if (!ss.eof() || ss.fail())
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse \" << s << \" as int\";
        throw invalid_argument(err.str());
    }
    return result;
}

bool cppgenParseBool(std::string s, int& lineNumber)
{
    using namespace std;
    if (s.compare("1") == 0 || lowercase(s).compare("true") == 0)
    {
        return true;
    }
    else if (s.compare("0") == 0 || lowercase(s).compare("false") == 0)
    {
        return false;
    }

    stringstream err;
    err << \"Parser Error on line \" << lineNumber << \": Could not parse \" << s << \" as bool\";
    throw invalid_argument(err.str());
}

std::string cppgenParseString(std::string s, int& lineNumber)
{
    return s;
}

float cppgenParseFloat(std::string s, int& lineNumber)
{
    using namespace std;
    stringstream ss(s);
    float result;
    ss >> result;
    if (!ss.eof() || ss.fail())
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse \" << s << \" as float\";
        throw invalid_argument(err.str());
    }
    return result;
}

std::vector<int> cppgenParseIntList(std::vector<std::string> strings, int& lineNumber)
{
    using namespace std;
    if (strings.size() == 0)
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse empty string as list\";
        throw invalid_argument(err.str());
    }
    vector<int> resval;
    for (unsigned int i = 0; i < strings.size(); i++)
    {
        resval.push_back(cppgenParseInt(strings[i], lineNumber));
    }
    return resval;
}

std::vector<bool> cppgenParseBoolList(std::vector<std::string> strings, int& lineNumber)
{
    using namespace std;
    if (strings.size() == 0)
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse empty string as list\";
        throw invalid_argument(err.str());
    }
    vector<bool> resval;
    for (unsigned int i = 0; i < strings.size(); i++)
    {
        resval.push_back(cppgenParseBool(strings[i], lineNumber));
    }
    return resval;
}

std::vector<std::string> cppgenParseStringList(std::vector<std::string> strings, int& lineNumber)
{
    using namespace std;
    if (strings.size() == 0)
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse empty string as list\";
        throw invalid_argument(err.str());
    }
    vector<string> resval;
    for (unsigned int i = 0; i < strings.size(); i++)
    {
        resval.push_back(cppgenParseString(strings[i], lineNumber));
    }
    return resval;
}

std::vector<float> cppgenParseFloatList(std::vector<std::string> strings, int& lineNumber)
{
    using namespace std;
    if (strings.size() == 0)
    {
        stringstream err;
        err << \"Parser Error on line \" << lineNumber << \": Could not parse empty string as list\";
        throw invalid_argument(err.str());
    }
    vector<float> resval;
    for (unsigned int i = 0; i < strings.size(); i++)
    {
        resval.push_back(cppgenParseFloat(strings[i], lineNumber));
    }
    return resval;
}

std::string readLine(std::ifstream &f)
{
    using namespace std;
    if (f.eof())
    {
        throw 1;
    }
    string result;
    getline(f, result);
    if (f.bad())
    {
        throw runtime_error("IO Error: Unknown problem when reading input file");
    }
    return result;
}

void seek(std::ifstream &f, std::streampos pos)
{
    using namespace std;
    f.seekg(pos);
    if (f.bad())
    {
        throw runtime_error("IO Error: Unknown problem when reading input file");
    }
}

std::streampos getFilePointer(std::ifstream &f)
{
    using namespace std;
    streampos pos = f.tellg();
    if (pos == -1)
    {
        throw runtime_error("IO Error: Unknown problem when reading input file");
    }
    return pos;
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
