Overview
========

The Heimer script takes a format file and generates a parser which will parse
files for the format specified by the format file. It supports generating parser
code in Python, C++, and Java and can be extended to other languages in the
future.

Terminology
===========

The script is somewhat confusing to understand, since it parses a format file to
generate a parser that parses files of that format. Therefore, the following
terminology will be used in this specification to make it clear what is being
referred to.

    Figure of I/O sequence:
    ( Format File ) => | Heimer Script | => ( Parser )
    ( Input File  ) => | Parser | => ( User Actions )

**Format File**: 
This file specifies the format of the file that the Parser being generated will
is required to parse.

**Heimer Script**:  
The script that will generate a parser from the provided Format File.

**Parser**:  
The generated parser in a particular language. It should be able to parse files
of the format specified in the Format File.

**Input File**:  
The input file to the Parser. The Parser should be able to parse this file and
run any additional user code.

**User Actions**:  
Any actions that additional user code within the Parser take.

Format File format
==================

The Format File consists of 4 tags, enclosed by angled brackets, and the
corresponding information under each tag.

**\<head\>**  
    Contains Heimer-specific options and flags.

**\<options\>**  
    Contains the command-line options that the generated Parser will be able to
    handle.

**\<objects\>**  
    Specifies different object formats. Each object will be represented as a
    class in the Parser and will be parsed according to the format specified in
    this section.

**\<body\>**  
    Specifies the format for the entire input file in terms of the objects
    specified under the **\<objects\>** tag, or with primitive data types.

The \<head\> tag
==============

The **\<head\>** tag contains Heimer-specific options and flags. The supported
flags are noted here:

delimiter "[string]"
-------------------
This sets the delimiter string used throughout the parser. For instance,

    <head>
    delimiter ","

sets the global delimiter as a single comma, so a line 0,1,2,3 will be tokenized
as ["0", "1", "2", "3"].

The \<options\> tag
=================

The optional **\<options\>** tag designates how to parse command line options in 
the generated program. Each line under the <options> tag must be of the format

    FLAG_CHAR ARG_NAME PRIMITIVE_TYPE

where `FLAG` is the flag designating the command line option, `ARG_NAME` is the
variable name used to store the value, and `PRIMITIVE_TYPE` is one of int, bool
or string. For instance,

    <options>
    c count int

lets the script know that -c is a command line option that is followed by an 
`int`. The generated Parser will parse the text following -c as an integer and
store the result in a global variable called `count`.

The \<objects\> tag
===================

Information under the **\<objects\>** tag denotes how particular lines in the
Input File will be parsed into objects in the generated Parser. These
specifications follow the format:

    <objects>
    OBJECT1_NAME
        LINE1
        LINE2
        ...
    OBJECT2_NAME
        LINE1
        LINE2
        ...

where `OBJECT#_NAME` is a string indicating the name of a particular object and
`LINE#` are the different line formats that forms this object. 

A line format follows this basic format:

    <objects>
    OBJECT_NAME
        FIELD1_NAME:FIELD1_TYPE FIELD2_NAME:FIELD2_TYPE
        FIELD3_NAME:FIELD3_TYPE
        FIELD4_NAME:FIELD4_TYPE

where each field is a colon-separated quantity specifying a name and type for
the field. The name may not be repeated within an object and the type can be any
primitive type (int, float, string, bool, list\<primitive\>) or any previously
defined object type.

Each line may contain multiple fields, and each object may contain multiple
lines. For example, suppose the format of a simple 2D Triangle was desired. A
valid format would be:

    <objects>
    Triangle
        x1:int y1:int
        x2:int y2:int
        x3:int y3:int

Then, the generated Parser would recognize this input as a `Triangle` object:

    1 2
    3 4
    5 6

But not this:

    1 2 3
    4 5
    3 5

since the first line has more than just 2 ints. Note that this assumes that the
delimiter above in the **\<head\>** tag was set to a space.

Parsing empty lines
-------------------

Line formats may also be empty. In this case, the generated Parser will expect
there to be an empty line in the input file when parsing the associated object.
For example, suppose this was an object format:

    <object>
    Line
        x1:int x2:int

        x3:int x4:int

Then, the generated Parser would recognize this input as a `Line` object:

    1 2

    3 4

But not this:

    1 2
    3 4

since there is no empty line between the first line and the second.

Parsing repetitive lines
------------------------

Sometimes, a particular line format is repeated several times to form an object.
In this case, a special syntax is used to indicate the repetition. For example,
suppose an `Path` object was desired which is composed of a list of `Point`
objects. A valid format would be:

    <object>
    Point
        x:int y:int
    Path
        points:Point:*

Note the additional component in the first and only field under `Path`. This
third component is the "repetition string", which indicates how many times a
Point should be matched. In this case, the `*` indicates that the generated
Parser should continue matching Point's until it cannot anymore.

Therefore, the generated Parser would recognize this input as a `Path` object:

    1 2
    3 4
    5 6
    1 2
    3 4

But it would only recognize the first half of this input as a `Path` object:

    1 2
    3 4

    5 6
    4 2

since there is a newline separating the first set of points and the second.

The "repetition string" can be any of the following values:

**`*`**:  
Indicates that the particular object may be repeated 0 or more times.

**`+`**:  
Indicates that the particular object may be repeated 1 or more times.

`integer`:  
Indicates that the particular object will be repeated an integral number of
times.

`variable`:  
Indicates that the particular object will be repeated a variable number of
times. This variable may be any previously defined integer number within the
object.

**WARNING**: A line with a field with this repetition string may only contain one field
! If there is more than one it will be a Format File error!

Newline between repetitive lines
--------------------------------

A simple tweak to the above syntax allows the generated Parser to expect a
newline BETWEEN repeated lines. For example, suppose the same `Path` object was
being parsed, but a newline was expected between each point. A valid format
would be:

    <object>
    Point
        x:int y:int
    Path
        points:Point:*!

Note the `!` after the "repetition string". Therefore, the generated Parser
would recognize this input as a `Path` object:

    1 2

    3 4

    5 6

But only the first point in this input:

    1 2
    3 4
    5 6

Since the parser would expect a newline after parsing the first point.

The \<body\> tag
================

The **\<body\>** tag is identical to the objects tag, except that it defines
only one object, the **Body** object. Therefore, each line under this tag is
simply a line format of the same style as those under objects in the **\<object
\>** tag. When the generated Parser starts to parse an input file, it would
expect the input file to have the overall format of the lines under the
**\<body\>** tag.

Comments
========

Comments are allowed in the Format File. Comments are preceded with the `#`
symbol. Anything after a `#` is ignored in the Format File.

Examples
========

A couple of examples are listed here showcasing the abilities of the Heimer
Script and the flexibility of the Format File.

Graph Parser
------------

    # Parses an input file listing several graphs

    <head>
    delimiter ","

    <objects>
    Adjacency
        vertex:int neighbors:list(int)

    Graph
        name:string
        adjacencies:Adjacency:+

    <body>
    graphs:Graph:+!

The generated Parser can parse inputs such as this:

    simple_graph
    0,1,2,3
    1,0
    2,0,3
    3,0,2

    unconnected_graph
    0,2,3
    1
    2,0,3,4,5
    3,0,2
    4,2,5
    5,2,4

Which will generate two `Graph` objects stored in `Body.graphs`. Each graph has
a name as well as a list of `Adjacency` objects which stores a vertex and its
neighbors.

Parsing words
-------------

    # Parses a file a known number of lines of words
    <body>
    count:int
    lines:list(string):count

The generated Parser can parse inputs such as this:

    3
    all your base
    belongs
    to us

Which will store `3` in `Body.count` and the various lines in `Body.lines`. Each
line contains a list of strings for the various words. Note that the above
syntax varies depending on the language the generated Parser is in.

