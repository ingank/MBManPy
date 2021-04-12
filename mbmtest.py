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
    description='Ein Programm zur Anwendung des Moduls mbman.py'
)

parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("-x", "--expunge", action="store_true")
parser.add_argument("-s", "--server")
parser.add_argument("-u", "--username")
parser.add_argument("-p", "--passphrase")
parser.add_argument("-m", "--mailbox")
parser.add_argument("-l", "--limit")
parser.add_argument("--uid")
parser.add_argument("--connect", action="store_true")
parser.add_argument("--login", action="store_true")
parser.add_argument("--get-mb-list", action="store_true")
parser.add_argument("--get-quota", action="store_true")
parser.add_argument("--get-info", action="store_true")
parser.add_argument("--get-message", action="store_true")
parser.add_argument("--autolimit", action="store_true")
parser.add_argument("--check-validity", action="store_true")

parser.print_help()
args = parser.parse_args()
print(args)
