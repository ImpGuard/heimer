from fixtures import getTest

def getTests(extension):
    return [
        getTest(0, "graph", extension, 1),
        getTest(4, "graph", extension, 1),
        getTest(0, "whitespace", extension, 1),
        getTest(4, "whitespace", extension, 1),
        getTest(4, "whitespace", extension, 2),
        getTest(4, "whitespace", extension, 3),
        getTest(0, "repetition", extension, 1),
        getTest(0, "repetition", extension, 2),
        getTest(0, "repetition", extension, 3),
        getTest(4, "repetition", extension, 1),
        getTest(4, "repetition", extension, 2),
        getTest(4, "repetition", extension, 3),
        getTest(0, "everything", extension, 1)
    ]

def getParserTests(extension):
    return [
        getTest(2, "invalidChars1", extension, 0),
        getTest(2, "invalidChars2", extension, 0),
        getTest(2, "invalidTags", extension, 0),
        getTest(2, "noBody", extension, 0)
    ]
