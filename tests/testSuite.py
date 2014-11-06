from fixtures import getTest

def getTests(extension):
    return [
        getTest(0, "graph", extension, 1),
        getTest(4, "graph", extension, 1),
        getTest(0, "whitespace", extension, 1)
    ]
