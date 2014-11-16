import sys
from os.path import join
from optparse import OptionParser

USAGE = "usage: %prog [options] outputName"

outputFile = None

def writeLine(line):
    outputFile.write(line + "\n")

if __name__ == "__main__":
    optParser = OptionParser(usage = USAGE)
    optParser.add_option( "-s", "--source", action = "store", dest = "sourceDir", default="src",
            help = "Specifies the location of the source directory" )
    optParser.add_option( "-i", "--import", action = "store", dest = "importFileName",
            default = "compile/importFile",
            help = "Specifies the location of the import file relative to the source directory" )
    optParser.add_option( "-f", "--files", action = "store", dest = "fileOrderFileName",
            default = "compile/fileOrder",
            help = "Specifies the location of the file order file relative to the source directory" )
    (options, args) = optParser.parse_args()

    if len(args) != 1:
        optParser.print_help()
        sys.exit(1)

    sourceDir = options.sourceDir
    outputFile = open(args[0], "w")
    fileOrderFile = open(join(sourceDir, options.fileOrderFileName), "r")
    importFile = open(join(sourceDir, options.importFileName), "r")

    # Write script hashbang
    writeLine("#!/usr/bin/env python\n")

    # Write import lines
    for line in importFile:
        if line == "":
            continue
        items = line.rstrip().split(" ")
        if len(items) == 1:
            # Single item, simply import it
            writeLine("import " + line.rstrip())
        else:
            # Multiple item, importing multiple things
            result = "from " + items[0] + " import "
            for field in items[1:]:
                result += field + ", "
            writeLine(result[:-2])

    writeLine("")
    importFile.close()

    # Write files in the order specified
    for line in fileOrderFile:
        fileName = line.rstrip() + ".py"
        f = open(join(sourceDir, fileName), "r")
        for srcLine in f:
            if srcLine.lstrip().startswith("import") or srcLine.startswith("from"):
                continue
            writeLine(srcLine.rstrip())
        f.close()
        writeLine("")
    fileOrderFile.close()
