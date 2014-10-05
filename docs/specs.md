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

where FLAG is the flag designating the command line option, ARG_NAME is the
variable name used to store the value, and PRIMITIVE_TYPE is one of int, bool
or string. For instance,

    <options>
    c count int

lets the script know that -c is a command line option that is followed by an 
`int`. The generated Parser will parse the text following -c as an integer and
store the result in a global variable called `count`.

The <single> tag
================

Information under the <single> tag denotes how single lines are parsed into
objects. These specifications follow the format:

    <single>
    CLASS_NAME
        VARIABLE_NAME:PRIMITIVE_TYPE VARIABLE_NAME:PRIMITIVE_TYPE (...and so on...)
    CLASS_NAME
        (...and so on...)

where CLASS_NAME is a string indicating the name of a class, VARIABLE_NAME
is the name of a variable, and PRIMITIVE_TYPE is one of int, string, bool,
list(int), list(bool), or list(string). For instance,

    <single>
    Point2D
        x:int y:int
    Point3D
        x:int y:int z:int

will generate two classes: Point2D and Point3D, the first of which has
integer x and y values, and the second of which has integer x, y and
z values.

When the generated parser sees the line 1 2 3, it will parse it into a
Point3D object with the fields set as x = 1, y = 2, and z = 3.
Similarly, when the generated parser sees the line 4 5, it will parse it as a
Point2D with fields x = 4 and y = 5.

The <multiple> tag
==================

Information under the <multiple> tag denotes how multiple lines are parsed into
objects. These specifications follow the format:

    <multiple>
    CLASS_NAME
        VARIABLE_NAME:TYPE(:LINE_SPECIFIER)
        VARIABLE_NAME:TYPE(:LINE_SPECIFIER)
        (...and so on...)
    CLASS_NAME
        (...and so on...)

Just as before, CLASS_NAME is a string indicating the name of a class and
VARIABLE_NAME specifies the name of a field of type TYPE. However, under
the <multiple tag>, TYPE is not restricted to only PRIMITIVE_TYPE -- a
TYPE can also be any abstract CLASS_NAME already specified previously in
the <multiple> tag or anywhere in the <single> tag.

TYPE is either a primitive type or a previously named class. The optional
LINE_SPECIFIER after the TYPE specifies the number of TYPE instances we
expect this class to contain. This NUMBER can either be a raw integer
literal, a previously defined integer variable, or one of "+" or "*". "+"
denotes that one or more TYPEs must be parsed, and "*" allows for any
number (including none) to be parsed. These operators are greedy, and will
continue parsing until it reaches the end of file, or an item that
cannot be parsed as a TYPE.

Additionally, appending "!" to the end of the LINE_SPECIFIER lets Heimer know that
there is an extra newline character ("\n") between each parsed item. Lets consider
the following example, where a Point2D is an "x y" pair on a single line.

Lets consider the following example, where a Point2D is an "x y" pair on a
single line (as defined in the <single> example above).

    <multiple>
    Line2D
        p1:Point2D
        p2:Point2D
    Path2D
        lines:Line2D:+!

In this case, a Path2D has a collection of Line2D that consists of at least 1
line, as denoted by the "+". Additionally, each Line2D is separated by an
additional newline character, as denoted by the "!". Thus, the following would
parse as a Path2D with 3 lines:

    0 0
    1 2

    1 2
    4 0

    4 0
    2 1

The resulting parser would ultimately create a Path2D object containing a
collection (dependent on the language) of Line2D objects, each of which would
contain the corresponding p1 and p2 Point2D objects and their x, y values.

    Path2D
        Line2D
            p1
                x = 0
                y = 0
            p2
                x = 1
                y = 2
        Line2D
            p1
                x = 1
                y = 2
            p2
                x = 4
                y = 0
        Line2D
            p1
                x = 4
                y = 0
            p2
                x = 2
                y = 1

The <body> tag
==============

The body tag describes the overall layout of the input file, in terms of both
primitives and classes specified in the previous sections. Information under the
<body> tag follows this format:

    <body>
    VARIABLE_NAME:TYPE(:LINE_SPECIFIER)
    VARIABLE_NAME:TYPE(:LINE_SPECIFIER)
    (...and so on...)

where VARIABLE_NAME is a string indicating the name of a global variable in the
generated code that will be used to store the data. As with the <multiple> tag, the
TYPE specifies the type of the variable. Again, if the variable should contain
multiple instances of the type, the LINE_SPECIFIER denotes how many instances to
parse. Additionally, newline characters between lines in the <body> tag denote that
an additional newline separates lists of items.

Lets consider the following input file format, where there are two "sections": the
number of 2D points followed by the coordinates of the 2D points, each on a separate
line, and then the number of 3D points, followed by the coordinates of the 3D points,
each on a separate line. An additional newline separates these two sections. An input
file might look like this:

    2
    1 3
    3 7

    3
    1 6 4
    1 8 8
    1 7 0

Note that there is an additional newline between "3 7" and "3". Thus, a newline must
be added between the declaration of 2D points and 3D points. We would use the
following Heimer specification:

    <body>
    numPoints2D:int
    points2d:Point2D:numPoints2D

    numPoints3D:int
    points3d:Point3D:numPoints3D

The final parsed values for the given input file would be the following:

    numPoints2D = 2

    points2d = [
        Point2D
            x = 1
            y = 3
        Point2D
            x = 3
            y = 7
    ]

    numPoints3D = 2

    points3d = [
        Point3D
            x = 1
            y = 6
            z = 4
        Point3D
            x = 1
            y = 8
            z = 8
        Point3D
            x = 1
            y = 7
            z = 0
    ]
