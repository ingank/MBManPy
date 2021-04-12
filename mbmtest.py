#
# mbmtest.py
#
# Ein Programm zur Anwendung von mbman.py
#
# 2021 by Ingolf Ankert
#

import mbman
import argparse

parser = argparse.ArgumentParser(
    description='Ein Programm zur Anwendung des Moduls mbman.py',
    add_help=False,
    argument_default='-h'
)

parser.add_argument("-h", "--help")

args = parser.parse_args()
