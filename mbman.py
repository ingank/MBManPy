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
        self.connected = None
        self.authenticated = None
        self.selected = None
        self.host = None
        self.user = None
        self.passwd = None
        self.welcome = None
        self.readonly = None

    def connect(self, host=None):
        """Verbindung zu einem IMAP4-Server herstellen.

        welcome = <instance>.connect(server)

        'welcome' beinhaltet die Willkommensantwort des Servers
        'host' ist eine IMAP4-Serveradresse
        """
        if self.connected:
            return None
        if not host:
            host = self.host
        if not host:
            return None
        self.connection = IMAPClient(host=host)
        self.host = host
        self.connected = True
        return self.connection.welcome

    def login(self, user=None, passwd=None):
        """Auf einem IMAP4 Server einloggen.

        response = <instance>.login(user, passwd)

        'response' beinhaltet die letzte Antwort des Servers auf den Loginversuch
        'user' Benutzername des Accounts
        'passwd' dazugehöriges Passwort
        """
        if not self.connected:
            return None
        if not user:
            user = self.user
        if not user:
            return None
        if not passwd:
            passwd = self.passwd
        if not passwd:
            return None
        response = self.connection.login(username=user, password=passwd)
        self.user = user
        self.passwd = passwd
        self.authenticated = True
        return response

    def select(self, folder='INBOX'):
        """Einen Mailbox-Ordner (lesend und schreibend) anwählen.

        response = <instance>.select(folder='INBOX')

        'response' beinhaltet die letzte Antwort des Servers auf den IMAP-Befehl 'SELECT'
        'folder' Name des anzuwählenden Ordners. Bei Nichtangabe, wird standardmäßig 'INBOX' angewählt
        """
        if not self.authenticated:
            return None
        response = self.connection.select_folder(folder)
        self.selected = True
        self.readonly = False
        return response

    def examine(self, folder='INBOX'):
        """Einen Mailbox-Ordner (nur lesend) anwählen.

        response = <instance>.examine(folder='INBOX')

        'response' beinhaltet die letzte Antwort des Servers auf den IMAP-Befehl 'EXAMINE'
        'folder' Name des anzuwählenden Ordners. Bei Nichtangabe, wird standardmäßig 'INBOX' angewählt
        """
        if not self.authenticated:
            return None
        response = self.connection.select_folder(folder, readonly=True)
        self.selected = True
        self.readonly = True
        return response

    def close(self):
        """Aktuellen Mailbox-Ordner schließen (kein Logout).

        response = <instance>.close()

        'response' beinhaltet die Antwort des Servers auf den CLOSE-Befehl
        'response' beinhaltet None, wenn keine Mailbox angewählt war
        """
        if not self.selected:
            return None
        response = self.connection.close_folder()
        self.selected = False
        self.readonly = False
        return response

    def logout(self):
        """Verbindung zum Server komplett abbauen.
        Dabei ist unerheblich, ob eine Mailbox angewählt ist.
        Die Verbindung wird in jedem Fall kontrolliert abgebaut.

        response = <instance>.logout()

        'response' beinhaltet die Antwort des Servers auf den LOGOUT-Befehl
        'response' beinhaltet None, wenn keine Client-Server-Verbindung bestand
        """
        if not self.connected:
            return None
        self.close()
        response = self.connection.logout()
        self.authenticated = False
        self.connected = False
        return response

    def list_folders(self):
        """Liefert eine Liste aller Mailbox-Ordner des aktuellen Benutzers.

        response = <instance>.list_folders()
        """
        if not self.connected:
            return None
        if not self.authenticated:
            return None
        ret = []
        for (dummy, dummy, z) in self.connection.list_folders():
            ret.append(z)
        return ret

    def list_messages(self):
        """Liefert eine Liste der UID's aller Nachrichten des aktuellen Mailbox-Ordners.

        response = <instance>.list_messages()
        """
        if not self.connected:
            return None
        if not self.authenticated:
            return None
        if not self.selected:
            return None
        response = self.connection.search()
        return response

    def fetch_message(self, uid):
        # fetch hole message as string
        return

    def save_message(self, uid):
        # fetch message and save it to backup-file
        return


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
    parser.add_argument("--select", nargs='?', type=str, metavar="foo", help="select specific mailbox", const="INBOX")
    parser.add_argument("--examine", nargs='?', type=str, metavar="foo", help="select specific mailbox readonly", const="INBOX")
    parser.add_argument("--list-folders", action="store_true", help="get a list of mailbox folders available for the logged in user")
    parser.add_argument("--list-messages", action="store_true", help="get a list of message uid's available in selected mailbox folder")
    args = parser.parse_args()

    try:
        mb = MBMan()
        if (args.print_args):
            print(args)
        if (args.connect):
            print(mb.connect(host=args.connect))
        if (args.login):
            print(mb.login(user=args.login[0], passwd=args.login[1]))
        if (args.select):
            print(mb.select(folder=args.select))
        if (args.examine):
            print(mb.examine(folder=args.examine))
        if (args.list_folders):
            print(mb.list_folders())
        if (args.list_messages):
            print(mb.list_messages())
        if (mb.connected):
            mb.logout()

    except:
        mb.logout()
