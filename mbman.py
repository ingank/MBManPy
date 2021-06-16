#
# mbman.py
#
# Eine Mailbox Management API in Python.
#
# 2021 by Ingolf Ankert
#

from imapclient import IMAPClient
import email
import os
import re
#import dumper


class MBMan:

    def __init__(self):
        self.passwd = None
        self.connected = None
        self.authenticated = None
        self.selected = None

    def connect(self, server):
        """Verbindung zu einem IMAP4 Server herstellen.

        (typ, [data]) = <instance>.connect(server)

        'typ' ist 'OK', wenn Verbindung erfolgreich
        'data' beinhaltet die Willkommensantwort des Servers
        'server' ist eine Serveradresse
        """
        self.connection = IMAPClient(host=server)
        self.connected = True

    def login(self, user, passwd):
        """Auf einem IMAP4 Server einloggen.

        (typ, [data]) = <instance>.login(user, passwd)

        'typ' ist 'OK', wenn Login erfolgreich
        'data' beinhaltet die letzte Antwort des Servers auf den Loginversuch
        'user' Benutzername zum gewünschten Account
        'passwd' dazugehöriges Passwort
        """
        self.connection.login(username=user, password=passwd)
        self.authenticated = True

    def close(self):
        """Aktuellen Mailbox-Ordner schließen (kein Logout).

        (typ, [data]) = <instance>.close()

        'typ' ist 'OK', wenn CLOSE erfolgreich
        'data' beinhaltet die Antwort des Servers auf den CLOSE-Befehl
        'typ' und 'data' werden auf None gesetzt, wenn keine Mailbox angewählt war        
        """
        if self.selected:
            self.connection.close_folder()
            self.selected = False

    def logout(self):
        """Verbindung zum Server komplett abbauen.
        Dabei ist unerheblich, ob eine Mailbox angewählt ist.
        Die Verbindung wird in jedem Fall kontrolliert abgebaut.

        (typ, [data]) = <instance>.logout()

        'typ' ist 'OK', wenn LOGOUT erfolgreich
        'data' beinhaltet die Antwort des Servers auf den LOGOUT-Befehl
        'typ' und 'data' werden auf None gesetzt, wenn keine Client-Server-Verbindung bestand        
        """
        if self.connection:
            if self.connected:
                if self.selected:
                    self.close()
                self.connection.logout()
                self.authenticated = False
                self.connected = False


if __name__ == "__main__":

    import logging

    logging.basicConfig(
        format='%(asctime)s - %(levelname)s: %(message)s',
        level=logging.DEBUG
    )

    import argparse

    parser = argparse.ArgumentParser(description='A Mailbox Management API in Python.')
    parser.add_argument("--print-args", action="store_true", help="print parsed command line arguments")
    parser.add_argument("--connect", type=str, metavar="foo", help="connect to server foo")
    parser.add_argument("--login", nargs=2, type=str, metavar=("foo", "bar"), help="login to account foo with password bar")
    args = parser.parse_args()

    try:
        mb = MBMan()
        if (args.print_args):
            print(args)
        if (args.connect):
            mb.connect(server=args.connect)
        if (args.login):
            mb.login(user=args.login[0], passwd=args.login[1])
    except:
        mb.logout()
        raise
    else:
        mb.logout()
