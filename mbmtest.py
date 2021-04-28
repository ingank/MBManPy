#
# mbmtest.py
#
# Ein Programm zur Anwendung von mbman.py
#
# 2021 by Ingolf Ankert
#

import mbman
import argparse


def main():
    args = parseArgs()
    mb = mbman.MBMan(args.debug)
    try:
        if (args.connect):
            print(mb.connect(server=args.server))
        if (args.login):
            print(mb.login(user=args.user, passwd=args.passwd))
        if (args.get_quota):
            usage, quota = mb.quota()
            print(usage, quota, " = ", usage/quota*100, "%")
        if (args.get_boxes):
            print(mb.boxes())
        if (args.select):
            if (args.mbox):
                print(mb.select(args.mbox))
        if (args.examine):
            if (args.mbox):
                print(mb.select(args.mbox, True))
        if (args.test):
            print(mb.db_save('681'))
    except:
        mb.logout()
        raise
    mb.logout()


def parseArgs():
    parser = argparse.ArgumentParser(description='A Python program using modul mbman.py')
    # Optionen
    parser.add_argument("-x", "--expunge", action="store_true", help="delete messages on server")
    parser.add_argument("-c", "--check-validity", action="store_true", help="check backup-files against server-data")
    parser.add_argument("-a", "--print-args", action="store_true", help="print parsed command line arguments")
    # Parameter
    parser.add_argument("-s", "--server", metavar="foo", help="given server name")
    parser.add_argument("-u", "--user", metavar="foo", help="given username")
    parser.add_argument("-p", "--passwd", metavar="foo", help="given password")
    parser.add_argument("-m", "--mbox", metavar="foo", help="select a mailbox")
    parser.add_argument("-l", "--limit", metavar="int", type=int, help="set limit to int percent")
    parser.add_argument("-i", "--uid", metavar="int", type=int, help="select message with uid int")
    parser.add_argument("-d", "--debug", metavar="int", type=int, help="set debug level to int", default=0)
    # Befehle
    parser.add_argument("--connect", action="store_true", help="connect to imap server")
    parser.add_argument("--login", action="store_true", help="login to an imap user account")
    parser.add_argument("--get-quota", action="store_true", help="print infos about quota and usage")
    parser.add_argument("--get-boxes", action="store_true", help="print a list of available mailboxes")
    parser.add_argument("--get-info", action="store_true", help="print some infos about the mbman object")
    parser.add_argument("--get-message", action="store_true", help="get a message from server")
    parser.add_argument("--select", action="store_true", help="select a specific mailbox (use with parameter '-m'")
    parser.add_argument("--examine", action="store_true", help="select a specific mailbox readonly")
    parser.add_argument("--autolimit", action="store_true", help="automatic limit and backup the mailbox")
    parser.add_argument("--test", action="store_true", help="test a new object function")
    #-#
    args = parser.parse_args()
    if (args.print_args):
        print(args)
    return args


if __name__ == "__main__":
    main()
