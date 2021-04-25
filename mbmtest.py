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
            print(mb.login(user=args.user, phrase=args.phrase))
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
            print(mb.db_path())
        if (args.watch):
            mb.idle()
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
    parser.add_argument("-s", "--server", metavar="foo", help="given server name is foo")
    parser.add_argument("-u", "--user", metavar="foo", help="given username is foo")
    parser.add_argument("-p", "--phrase", metavar="foo", help="given passphrase is foo")
    parser.add_argument("-m", "--mbox", metavar="foo", help="select mailbox foo")
    parser.add_argument("-l", "--limit", metavar="int", type=int, help="set limit to int percent")
    parser.add_argument("-i", "--uid", metavar="int", type=int, help="select message with uid int")
    parser.add_argument("-d", "--debug", metavar="int", type=int, help="set debug level to int", default=0)
    # Befehle
    parser.add_argument("-C", "--connect", action="store_true", help="connect to imap server")
    parser.add_argument("-L", "--login", action="store_true", help="login to an imap user account")
    parser.add_argument("-Q", "--get-quota", action="store_true", help="print infos about quota and usage")
    parser.add_argument("-B", "--get-boxes", action="store_true", help="print a list of available mailboxes")
    parser.add_argument("-I", "--get-info", action="store_true", help="print some infos about the mbman object")
    parser.add_argument("-M", "--get-message", action="store_true", help="get a message from server")
    parser.add_argument("-W", "--watch", action="store_true", help="idle connection and wait for server message")
    parser.add_argument("-S", "--select", action="store_true", help="select a specific mailbox")
    parser.add_argument("-E", "--examine", action="store_true", help="select a specific mailbox readonly")
    parser.add_argument("-A", "--autolimit", action="store_true", help="automatic limit an backup the mailbox")
    parser.add_argument("-T", "--test", action="store_true", help="test a new object function")
    #-#
    args = parser.parse_args()
    if (args.print_args):
        print(args)
    return args


if __name__ == "__main__":
    main()
