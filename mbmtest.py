#
# mbmtest.py
#
# Ein Programm zur Anwendung von mbman.py
#
# 2021 by Ingolf Ankert
#

import mbman
import sys
import getopt

arg_list = sys.argv[1:]  # erstes Argument der Kommndozeile und darauf folgende
short_opts = "?hmo:"
long_opts = ["Help", "My_file", "Output ="]

try:

    arguments, values = getopt.getopt(arg_list, short_opts, long_opts)

    for currentArgument, currentValue in arguments:

        if currentArgument in ("-?", "-h", "--Help"):
            print("Diplaying Help")

        elif currentArgument in ("-m", "--My_file"):
            print("Displaying file_name:", sys.argv[0])

        elif currentArgument in ("-o", "--Output"):
            print(("Enabling special output mode (% s)") % (currentValue))

except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
