from parser import StringConstants

class HeimerFormat:
    def __init__( self, objectModel ):
        self._model = objectModel
        # Make sure the user defined classes are of the correct format, else raise error.
        self._userClasses = dict()
        self._userClassNames = list()
        for c in self._model.classes:
            _assertValidName( c.name, self._userClasses )
            _assertValidClass( c, self._userClasses )
            self._userClasses[c.name] = c
            self._userClassNames.append(c.name)
        # Make sure the body is of the correct format.
        _assertValidClass( self._model.body, self._userClasses )
        self._body = HeimerFormatObject( self._model.body, self._userClasses )

    def lineDelimiter(self):
        return self._model.lineDelimiter

    def commandOptions(self):
        return self._model.commandOptions

    def classes(self):
        """ Return a list of tuples, where the tuple contains the class name and a dictionary with
        key-value pair of field name and field type (in string). """
        classes = []
        for className in self._userClassNames:
            c = self._userClasses[className]
            fields = dict()
            for line in c.lines:
                for field in line:
                    fields[field.name] = field.typeName
            classes.append( ( className, fields ) )
        return classes

    def body(self):
        return self._body


class HeimerFormatObject:
    def __init__( self, field, userClasses ):
        self._field = field
        self._userClasses = userClasses
        _assertValidType(field.typeName)
        self._class = None if self.isPrimitive else userClasses[field.typeName]
        self._lines = []
        self._variables = dict()
        # If it is a user defined class, recursively construct HeimerFormatObject from the variables
        # contained in the class.
        if self._class:
            for line in self._class.lines:
                l = []
                for var in line:
                    _assertValidName( var.name, self._variables )
                    obj = HeimerFormatObject( var, userClasses )
                    self._variables[var.name] = obj
                    l.append(obj)
                    # Make sure if the variable has a instance repetition mode, it is either an
                    # integer, a special symbol, or an integer variable already defined in this
                    # particular user class.
                    mode = obj.instanceRepetitionMode
                    if ( mode and type(mode) != int and \
                        mode != StringConstants.LINE_ONE_OR_MORE and \
                        mode != StringConstants.LINE_ZERO_OR_MORE and \
                        ( mode not in self._variables or \
                        not self._variables[mode].isInteger() ) ):
                        raise ValueError("Unknown repetition mode '%s': it must be either an integer, \
                            the symbol '+' or '*', or an int variable already defined in class." % mode)
                self._lines.append(l)

    def lines(self):
        return self._lines

    def newLinesAfterLastInstance(self):
        return self._field.newLinesAfterLastInstance

    def instanceRepetitionMode(self):
        mode = self._field.instanceRepetitionModeString
        try:
            return int(mode)
        except ValueError as e:
            return mode

    def shouldSeparateInstancesByAdditionalNewline(self):
        return self._field.shouldSeparateInstancesByAdditionalNewline

    def isPrimitive(self):
        return _isPrimitive(self._field.typeName)

    def isInteger(self):
        return self._field.typeName == StringConstants.INTEGER_TYPE

    def isFloat(self):
        return self._field.typeName == StringConstants.FLOAT_TYPE

    def isString(self):
        return self._field.typeName == StringConstants.STRING_TYPE

    def isBool(self):
        return self._field.typeName == StringConstants.BOOL_TYPE

    def isList(self):
        return _isList(self._field.typeName)

    def listType(self):
        if self.isList():
            return _listType(self._field.typeName)
        else:
            return None


def _isPrimitive(typeName):
    return typeName == StringConstants.INTEGER_TYPE or typeName == StringConstants.FLOAT_TYPE or \
        typeName == StringConstants.BOOL_TYPE or typeName == StringConstants.STRING_TYPE or \
        _isList(typeName)

def _isList(typeName):
    """ List is of the form 'list(listType)' where listType is a non-list primitive. """
    if typeName.find(StringConstants.LIST_TYPE) == 0 and \
        typeName[len(StringConstants.LIST_TYPE)] == "(" and \
        typeName[-1] == ")":
        listType = typeName[ len(StringConstants.LIST_TYPE) : len(typeName) - 1 ].strip()
        if _isPrimitive(listType) and not _isList(listType):
            return True
        else:
            return False
    return False

def _listType(typeName):
    if _isList(typeName):
        return typeName[ len(StringConstants.LIST_TYPE) : len(typeName) - 1 ].strip()
    else:
        return None

def _assertValidName( name, usedNames ):
    if name in usedNames:
        raise ValueError("Name conflict: User defined class/variable must have unique name, the name \
            '%s' is used more than once." % name)
    if _isPrimitive(name):
        raise ValueError("Name conflict: '%s' is a primitive type and cannot be used as the name \
            of user defined classes/variables." % name)

def _assertValidType( typeName, userClasses ):
    # Valid type if it's a user defined class
    if typeName in userClasses:
        return
    # Valid type if it's a primitive
    elif _isPrimitive(typeName):
        return
    # Invalid type if it's a list but the list type is not a non-list primitive
    elif ( typeName.find(StringConstants.LIST_TYPE) == 0 and \
            typeName[len(StringConstants.LIST_TYPE)] == "(" and \
            typeName[-1] == ")" ):
        # get the list type and remove whitespaces in the front and back
        listType = typeName[ len(StringConstants.LIST_TYPE) : len(typeName) - 1 ].strip()
        if not _isPrimitive(listType) or _isList(listType):
            raise ValueError("The type of a list can only be a non-list primitive type.")
        return
    # Else invalid type.
    raise ValueError("Unknown variable type '%s', it should either be a primitive type or \
        a user defined class." % typeName)

def _assertValidClass( c, userClasses ):
    # Verify that every field in the class follows the spec
    for line in c.lines:
        for index, field in enumerate(line):
            if _isPrimitive(field.typeName):
                # a list can only be the last field on a line
                if _isList(field.typeName) and ( index + 1 ) >= len(line):
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
