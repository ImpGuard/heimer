from parser import StringConstants, FieldDeclaration
from collections import OrderedDict

class HeimerFormat:
    def __init__( self, objectModel ):
        self._model = objectModel
        self._userClasses = OrderedDict()
        # The class names are stored twice because we want to perserve the ordering of the classes
        self._userClassNames = list()
        # Make sure the user defined classes are of the correct format, else raise error.
        for c in self._model.classes:
            _assertValidName( c.name, self._userClasses )
            _assertValidClass( c, self._userClasses )
            self._userClasses[c.name] = c
            self._userClassNames.append(c.name)
        self._body = FormatField( self._model.body, self._userClasses )

    def lineDelimiter(self):
        return self._model.lineDelimiter

    def commandLineOptions(self):
        return self._model.commandLineOptions

    def classes(self):
        """ Return a list of tuples, where the tuple contains the class name and a dictionary with
        key-value pair of field name and field type (in string). """
        classes = []
        for className in self._userClassNames:
            c = self._userClasses[className]
            fields = OrderedDict()
            for line in c.lines:
                for field in line:
                    fields[field.name] = field.typeName
            classes.append( ( className, fields ) )
        return classes

    def body(self):
        return self._body


class FormatField:
    def __init__( self, field, userClasses, parent=None ):
        self._field = field
        self._userClasses = userClasses
        self._parent = parent
        _assertValidType( field.typeName, userClasses )
        self._class = None if self.isPrimitive() else userClasses[field.typeName]
        self._lines = []
        self._variables = dict()
        # If it is a user defined class, recursively construct FormatField from the variables
        # contained in the class.
        if self._class:
            for line in self._class.lines:
                fields = []
                for var in line:
                    _assertValidName( var.name, self._variables.keys() + userClasses.keys() )
                    obj = FormatField( var, userClasses, parent=self )
                    self._variables[var.name] = obj
                    fields.append(obj)
                    # Make sure if the variable has a instance repetition mode, it is either an
                    # integer, a special symbol, or an integer variable already defined in this
                    # particular user class.
                    mode = obj.instanceRepetitionModeString()
                    if ( mode and type(mode) != int and \
                        mode != StringConstants.LINE_ONE_OR_MORE and \
                        mode != StringConstants.LINE_ZERO_OR_MORE and \
                        ( mode not in self._variables or \
                        not self._variables[mode].isInteger() ) ):
                        raise ValueError("Unknown repetition mode '%s': it must be either an integer, \
                            the symbol '+' or '*', or an int variable already defined in class." % mode)
                self._lines.append(FormatLine( fields, self ))

    def name(self):
        return self._field.name

    def typeName(self):
        return self._field.typeName

    def parent(self):
        """ The parent of this object """
        return self._parent

    def lines(self):
        """ Return a list of FormatLine objects, each representing a line in this field.
        Empty line denotes a line without any field. """
        return self._lines

    def instanceRepetitionModeString(self):
        mode = self._field.instanceRepetitionModeString
        try:
            return int(mode)
        except ValueError as e:
            return mode

    def shouldSeparateInstancesByAdditionalNewline(self):
        return self._field.shouldSeparateInstancesByAdditionalNewline

    def isPrimitive(self):
        return isPrimitive(self._field.typeName)

    def isInteger(self):
        return isInteger(self._field.typeName)

    def isFloat(self):
        return isFloat(self._field.typeName)

    def isString(self):
        return isString(self._field.typeName)

    def isBool(self):
        return isBool(self._field.typeName)

    def isList(self):
        return isList(self._field.typeName)

    def listType(self):
        if self.isList():
            return listType(self._field.typeName)
        else:
            return None

    def __str__(self):
        s = ""
        if self.isPrimitive():
            s += "%s:%s" % ( self.name(), self.typeName() )
            if self.instanceRepetitionModeString():
                s += ":%s" % self.instanceRepetitionModeString()
                if self.shouldSeparateInstancesByAdditionalNewline():
                    s += "!"
        else:
            for index, line in enumerate(self.lines()):
                s += str(line)
                if index < len(self.lines()) - 1:
                    s += "\n"
        return s

class FormatLine:
    """ Representing a line in a class declaration or body of the format file.
    May contains zero or more fields. """
    def __init__( self, fields, container ):
        self._fields = fields
        # container is the FormatField object representing the class field that contains this line
        self._container = container
        self._currentIndex = 0
        # Repetition string only makes sense when a line has exactly one field
        self._repetitionString = fields[0].instanceRepetitionModeString() if len(fields) == 1 else ""
        self._isSplitByNewline = fields[0].shouldSeparateInstancesByAdditionalNewline() if \
            len(fields) == 1 else "" if len(fields) == 1 else ""

    def container(self):
        return self._container

    def isEmpty(self):
        return len(self._fields) == 0

    def repetitionString(self):
        return self._repetitionString

    def isZeroOrMoreRepetition(self):
        return self._repetitionString == StringConstants.LINE_ZERO_OR_MORE

    def isONEOrMoreRepetition(self):
        return self._repetitionString == StringConstants.LINE_ONE_OR_MORE

    def isIntegerRepetition(self):
        try:
            int(self._repetitionString)
            return True
        except ValueError as e:
            # Failed to cast to int, it's not int
            return False

    def isVariableRepetition(self):
        return ( not self.isZeroOrMoreRepetition() and
            not self.isONEOrMoreRepetition() and
            not self.isIntegerRepetition() )

    def isSplitByNewline(self):
        return self._isSplitByNewline

    def __iter__(self):
        return self

    def next(self):
        if self._currentIndex < len(self._fields):
            self._currentIndex += 1
            return self._fields[self._currentIndex - 1]
        else:
            # Reset the counter so we can use this in more than one for loop
            self._currentIndex = 0
            raise StopIteration

    def __str__(self):
        s = ""
        for f in self:
            s += str(f) + " "
        return s

def isPrimitive(typeName):
    return typeName == StringConstants.INTEGER_TYPE or typeName == StringConstants.FLOAT_TYPE or \
        typeName == StringConstants.BOOL_TYPE or typeName == StringConstants.STRING_TYPE or \
        isList(typeName)

def isInteger(typeName):
    return typeName == StringConstants.INTEGER_TYPE

def isFloat(typeName):
    return typeName == StringConstants.FLOAT_TYPE

def isString(typeName):
    return typeName == StringConstants.STRING_TYPE

def isBool(typeName):
    return typeName == StringConstants.BOOL_TYPE

def isList(typeName):
    """ List is of the form 'list(listType)' where listType is a non-list primitive. """
    if len(typeName) <= 4:
        return False
    if typeName.find(StringConstants.LIST_TYPE) == 0 and \
        typeName[len(StringConstants.LIST_TYPE)] == "(" and \
        typeName[-1] == ")":
        listType = typeName[ len(StringConstants.LIST_TYPE) + 1 : len(typeName) - 1 ].strip()
        if isPrimitive(listType) and not isList(listType):
            return True
        else:
            return False
    return False

def listType(typeName):
    if isList(typeName):
        return typeName[ len(StringConstants.LIST_TYPE) + 1 : len(typeName) - 1 ].strip()
    else:
        return None

def _assertValidName( name, usedNames ):
    """ Verify a name isn't already used by another user defined class or field. """
    if name in usedNames:
        raise ValueError("Name conflict: User defined class/field must have unique name, the name \
            '%s' is used more than once." % name)
    if isPrimitive(name):
        raise ValueError("Name conflict: '%s' is a primitive type and cannot be used as the name \
            of user defined classes/fields." % name)

def _assertValidType( typeName, userClasses ):
    # Valid type if it's a user defined class
    if typeName in userClasses:
        return
    # Valid type if it's a primitive
    elif isPrimitive(typeName):
        return
    # Invalid type if it's a list but the list type is not a non-list primitive
    elif ( typeName.find(StringConstants.LIST_TYPE) == 0 and \
            typeName[len(StringConstants.LIST_TYPE)] == "(" and \
            typeName[-1] == ")" ):
        # get the list type and remove whitespaces in the front and back
        listType = typeName[ len(StringConstants.LIST_TYPE) + 1 : len(typeName) - 1 ].strip()
        if not isPrimitive(listType) or isList(listType):
            raise ValueError("The type of a list can only be a non-list primitive type.")
        return
    # Else invalid type.
    raise ValueError("Unknown field type '%s', it should either be a primitive type or \
        a user defined class." % typeName)

def _assertValidClass( c, userClasses ):
    # Verify that every field in the class follows the spec
    for line in c.lines:
        for index, field in enumerate(line):
            if isPrimitive(field.typeName):
                # a list can only be the last field on a line
                if isList(field.typeName) and ( index + 1 ) < len(line):
                    raise ValueError("Format error in user defined class '%s': list can only be the \
                        last field on a line." % c.name)
            else:
                if field.typeName not in userClasses:
                    raise ValueError("Format error in user defined class '%s': unknown field type '%s', \
                        all types must be either primitive type or a already defined user class."
                        % ( c.name, field.typeName ))
                # There is more than one field on this line
                if len(line) > 1:
                    raise ValueError("Format error in user defined class '%s': unexpected field \
                        type '%s', there can be exactly one field with user defined class as type in \
                        each line." % ( c.name, field.tpyName))

def getFormat(fileName="examples/graph_example"):
    from parser import HeimerFormatFileParser
    p = HeimerFormatFileParser(fileName)
    return HeimerFormat(p.objectModel)
