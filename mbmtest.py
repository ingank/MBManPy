#
# mbmtest.py
#
# Ein Programm zur Anwendung von mbman.py
#
# 2021 by Ingolf Ankert
#

import mbman
import argparse

parser = argparse.ArgumentParser(description='A Python program using modul mbman.py')

# Optionen
parser.add_argument("-x", "--expunge", action="store_true", help="delete messages on server")
parser.add_argument("-c", "--check-validity", action="store_true", help="check backup-files against server-data")

# Parameter
parser.add_argument("-s", "--server", metavar="foo", help="given server name is foo")
parser.add_argument("-u", "--user", metavar="foo", help="given username is foo")
parser.add_argument("-p", "--pass", metavar="foo", help="given passphrase is foo")
parser.add_argument("-m", "--mbox", metavar="foo", help="select mailbox foo")
parser.add_argument("-l", "--limit", metavar="int", help="set limit to int percent")
parser.add_argument("-i", "--uid", metavar="int", help="select message with uid int")
parser.add_argument("-d", "--debug", metavar="int", help="set debug level to int", default=0)

# Befehle
parser.add_argument("-C", "--connect", action="store_true", help="connect to imap server")
parser.add_argument("-L", "--login", action="store_true", help="login to an imap user account")
parser.add_argument("-B", "--get-boxes", action="store_true", help="print a list of available mailboxes")
parser.add_argument("-Q", "--get-quota", action="store_true", help="print infos about quota and usage")
parser.add_argument("-I", "--get-info", action="store_true", help="print some infos about the mbman object")
parser.add_argument("-M", "--get-message", action="store_true", help="get a message from server")
parser.add_argument("-A", "--autolimit", action="store_true", help="automatic limit an backup the mailbox")

args = parser.parse_args()
print(args)
