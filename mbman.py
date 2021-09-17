#
# mbman.py
#
# Eine Mailbox Management API in Python.
#
# 2021 by Ingolf Ankert
#

import imaplib
import os
import re
# import email


class MBMan:

    special_use = (
        # have a look at RFC 6154
        'All',
        'Archive',
        'Drafts',
        'Flagged',
        'Junk',
        'Sent',
        'Trash'
    )

    def __init__(self, debug, db_root, db_autosave=True, db_uidlength=8):
        imaplib.Debug = debug
        self.debug = debug
        self.server = None
        self.user = None
        self.passwd = None
        self.imap4 = None
        self.last_message = None
        self.last_message_path = None
        self.last_uid = None
        self.db_root = db_root
        self.db_uidlength = db_uidlength
        self.db_autosave = db_autosave
        self.db_path = None
        self.db_file = None
        self.mb_selected = None
        self.mb_readonly = None
        self.mb_uidvalidity = None
        self.mb_uidnext = None
        self.mb_flags = None
        self.mb_exists = None
        self.mb_recent = None

    def connect(self, server):
        """SSL-Verbindung zu einem IMAP4 Server herstellen.

        (typ, [data]) = <instance>.connect(server)

        'typ' ist 'OK', wenn Verbindung erfolgreich
        'data' beinhaltet die Willkommensantwort des Servers
        'server' ist eine Serveradresse
        """
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        wc = self.imap4.welcome
        typ, data = re.findall(br'\* ([A-Z-]+) (.*)?', wc)[0]
        typ = typ.decode('ascii')
        return (typ, [data])

    def login(self, user, passwd):
        """Auf einem IMAP4 Server einloggen.

        (typ, [data]) = <instance>.login(user, passwd)

        'typ' ist 'OK', wenn Login erfolgreich
        'data' beinhaltet die letzte Antwort des Servers auf den Loginversuch
        'user' Benutzername zum gewünschten Account
        'passwd' dazugehöriges Passwort
        """
        self.user = user
        self.passwd = passwd
        return self.imap4.login(user, passwd)

    def select(self, mailbox='INBOX', autosave=True, readonly=False):
        """Einen Mailbox-Ordner mittels SELECT anwählen.

        (typ, [data]) = <instance>.select(mailbox, autosave)

        'typ' ist 'OK', wenn SELECT erfolgreich war
        'data' beinhaltet die Antwort des Servers auf den SELECT-Befehl
        'mailbox' ist der Name des gewünschten Mailbox-Ordnerds. Voreinstellung: 'INBOX'
        'autosave' steuert, ob Nachrichten beim Herunterladen automatisch gesichert werden. Voreinstellung: True
        """
        (typ, data) = self.imap4.select(mailbox=mailbox, readonly=readonly)
        if (typ == 'OK'):
            self.mb_flags = self.imap4.response('FLAGS')[1]
            self.mb_exists = self.imap4.response('EXISTS')[1]
            self.mb_recent = self.imap4.response('RECENT')[1]
            self.mb_uidvalidity = self.imap4.response('UIDVALIDITY')[1]
            self.mb_uidnext = self.imap4.response('UIDNEXT')[1]
            self.mb_selected = mailbox
            self.mb_readonly = readonly
            self.db_autosave = autosave
            self.db_path = self.db_root + self.user + '/' + mailbox + '/'
            os.makedirs(self.db_path, exist_ok=True)
        return (typ, data)

    def examine(self, mailbox='INBOX', autosave=True):
        """Einen Mailbox-Ordner mittels EXAMINE anwählen.

        (typ, [data]) = <instance>.examine(mailbox, autosave)

        'typ' ist 'OK', wenn EXAMINE erfolgreich war
        'data' beinhaltet die Antwort des Servers auf den EXAMINE-Befehl
        'mailbox' ist der Name des gewünschten Mailbox-Ordners. Voreinstellung: 'INBOX'
        'autosave' steuert, ob Nachrichten beim Herunterladen automatisch gesichert werden. Voreinstellung: True

        Trivia: imaplib enthält keine Entsprechung für diesen IMAP-Befehl.
        """
        return self.select(mailbox=mailbox, autosave=autosave, readonly=True)

    def close(self):
        """Aktuellen Mailbox-Ordner schließen (kein Logout).

        (typ, [data]) = <instance>.close()

        'typ' ist 'OK', wenn CLOSE erfolgreich
        'data' beinhaltet die Antwort des Servers auf den CLOSE-Befehl
        'typ' und 'data' werden auf None gesetzt, wenn keine Mailbox angewählt war        
        """
        if not self.mb_selected:
            return None, None
        typ, data = self.imap4.close()
        self.mb_flags = None
        self.mb_exists = None
        self.mb_recent = None
        self.mb_uidvalidity = None
        self.mb_uidnext = None
        self.mb_selected = None
        self.mb_readonly = None
        self.db_autosave = None
        self.db_path = None
        self.db_file = None
        return typ, data

    def logout(self):
        """Verbindung zum Server komplett abbauen.
        Dabei ist unerheblich, ob eine Mailbox angewählt ist.
        Die Verbindung wird in jedem Fall kontrolliert abgebaut.

        (typ, [data]) = <instance>.logout()

        'typ' ist 'OK', wenn LOGOUT erfolgreich
        'data' beinhaltet die Antwort des Servers auf den LOGOUT-Befehl
        'typ' und 'data' werden auf None gesetzt, wenn keine Client-Server-Verbindung bestand        
        """
        if not self.imap4:
            return None, None
        typ, data = self.close()
        typ, data = self.imap4.logout()
        self.server = None
        self.user = None
        self.passwd = None
        self.imap4 = None
        return typ, data

    def state(self):
        return self.imap4.state

    def capability(self):
        return self.imap4.capability()

    def quota(self):
        """Speicherplatz des IMAP-Accounts abfragen.

        (usage, quota) = <instance>.quota()

        'usage' ist die Belegung des Speichers in Oktets (Byte)
        'quota' ist der für den aktuellen Account bereitgestellte Speicher in Oktets
        """
        quota_root = ('user/' + self.user)
        quota = self.imap4.getquota(quota_root)
        quota, quota = quota
        quota = quota[0].decode("ascii")
        usage, quota = re.findall(r"STORAGE (\d+) (\d+)", quota)[0]
        usage = int(usage) * 1024
        quota = int(quota) * 1024
        return usage, quota

    def folders(self):
        """Alle Mailbox-Ordner (Namen) abfragen.

        (typ, [folders]) = <instance>.folders()

        Wenn der LIST-Befehl erfolgreich war:
        'typ' ist 'OK'
        'folders' ist eine Liste aus Tupeln mit dem Inhalt (special_use, folder_name)
        'special_use' ist None, wenn der Ordner laut RFC6154 keine 'Special-Use Mailbox' ist
        'special_use' enthält das entsprechende Attribut, wenn der Ordner eine 'Special-Use Mailbox' ist
        'folder_name' enthält den Namen des Mailbox-Ordners

        Wenn der LIST-Befehl nicht erfolgreich war:
        'typ' ist ungleich 'OK'
        'folders' enthält die Serverantwort
        """
        (typ, response) = self.imap4.list()
        if not (typ == 'OK'):
            return (typ, response)
        folders = []
        for line in response:
            line = line.decode("ascii")
            line = re.split(' "." ', line)
            line = (
                re.findall(r"^\((.*)\)$", line[0])[0],
                re.findall(r"^\"(.*)\"$", line[1])[0]
            )
            special = None
            for su in self.special_use:
                if (line[0].find(su) != -1):
                    special = su
                    break
            folders.append((special, line[1]))
        return (typ, folders)

    def messages(self):
        return self.imap4.uid('fetch', '0:*', "RFC822.SIZE")

    def messages_all(self):
        return self.imap4.uid('fetch', '0:*', "ALL")

    def limit_list(self, lim=75):
        """Eine Liste mit UID's erzeugen,
        die nach Löschung der entsprechenden Nachrichten auf dem Server
        den genutzten Speicher genau unterhalb der limitierten Größe des
        IMAP-Accounts (Prozentuales Quota) einmessen würde.

        (uid_list) = <instance>.limit(lim)

        'uid_list' ist eine Liste bestehend aus UID's. Die Liste kann auch leer sein
        'lim' ist der Limit-Wert in Prozent und auf 75 voreingestellt
        """
        usage, quota = self.quota()
        lim = int((quota / 100) * lim)
        if (usage < lim):
            return []
        dummy, response = self.ls()
        uid_list = []
        for r in response:
            r = r.decode("ascii")
            r = re.findall(r"RFC822.SIZE (.*) UID (.*)\)$", r)
            size = int(r[0][0])
            uid = r[0][1]
            uid_list.append(uid)
            usage = usage - size
            if (usage < lim):
                break
        return uid_list

    def message_fetch(self, uid: str):
        """Eine Nachricht von der aktuellen Mailbox laden.

        message = <instance>.message_fetch(uid)

        'message' enthält die komplette Nachricht als String
        'uid' addressiert die gewünschte Nachricht

        Die Nachricht wird als --zu löschen-- markiert,
        wenn der Mailbox-Ordner mit select(..., readonly=False) gewählt wurde.
        Die selbige Nachricht wird endgültig gelöscht,
        sobald close() oder expunge() angewandt wird.

        Eine Kopie der Nachricht steht in self.last_message
        weiterhin zur Verfügung.
        """
        (typ, response) = self.imap4.uid('fetch', uid, "RFC822")
        if (typ == 'OK'):
            self.last_message = response[0][1].decode('ascii')
            self.last_uid = uid
            if self.db_autosave:
                uid_val = self.mb_uidvalidity[0].decode('ascii')
                length = len(uid)
                null_count = self.db_uidlength - length
                file_path = self.db_path
                file_path += uid_val + '_'
                file_path += '0' * null_count + uid
                file_path += '.eml'
                self.message_save(self.last_message, file_path)
                self.db_file = file_path
            if self.mb_readonly:
                return (typ, self.last_message)
            else:
                self.imap4.uid('store', uid, '+FLAGS', '\\Deleted')
                return (typ, self.last_message)
        else:
            return (typ, response)

    def message_save(self, message: str, path: str):
        """Nachricht in einer Datei speichern.

        Args:
            message (str): Die komplette Nachricht als String
            path (str): Der Dateiname als FQDN

        Returns:
            (bool): 'True', wenn Nachricht gespeichert wurde
        """
        try:
            f = open(path, "w")
            f.write(message)
            f.close()
            return True
        except Exception:
            return None

    def idle(self):
        # Copyright (c) 2012 Mathieu Lecarme
        # This code is licensed under the MIT license
        # # # TESTING
        connection = self.imap4
        tag = connection._new_tag()
        name = bytes('IDLE', 'ASCII')
        data = tag + b' ' + name
        connection.send(data + imaplib.CRLF)
        response = connection.readline()
        if response != b'+ idling\r\n':
            raise Exception("IDLE not handled? : %s" % response)
        self.loop = True
        while self.loop:
            try:
                resp = connection._get_response()
            except connection.abort:
                connection.done()
            else:
                uid, message = resp.split(maxsplit=2)[1:]
                if uid.isdigit():
                    yield uid, message
                elif uid != b'OK':
                    raise Exception('IDLE command error: %s %s' % (uid.decode(), message))
                # we have * OK still here

    def done(self):
        # Copyright (c) 2012 Mathieu Lecarme
        # This code is licensed under the MIT license
        # # # TESTING
        connection = self.imap4
        connection.send(b'DONE\r\n')
        connection.readline()
        self.loop = False


if __name__ == "__main__":

    import argparse
    import dumper

    db_root = os.environ['HOME'] + '/MBData/'

    parser = argparse.ArgumentParser(description='A Mailbox Management API in Python.')
    parser.add_argument("--args", action="store_true", help="print parsed command line arguments")
    parser.add_argument("--debug", type=int, metavar="foo", help="set debug level to foo", default=0)
    parser.add_argument("--dbroot", type=str, metavar="foo", help="set database root directory to foo", default=db_root)
    parser.add_argument("--autosave", action="store_true", help="save messages to database as they fetched from imap-server", default=True)
    parser.add_argument("--uidlength", type=int, metavar="foo", help="set length of uid in filename to size foo", default=8)
    parser.add_argument("--connect", type=str, metavar="foo", help="connect to server foo")
    parser.add_argument("--login", nargs=2, type=str, metavar=("foo", "bar"), help="login to account foo with password bar")
    parser.add_argument("--select", nargs='?', type=str, metavar="foo", help="select mailbox foo", const="INBOX")
    parser.add_argument("--examine", nargs='?', type=str, metavar="foo", help="select mailbox foo readonly", const="INBOX")
    parser.add_argument("--state", action="store_true", help="print infos about the actual state of connection")
    parser.add_argument("--capability", action="store_true", help="print infos about capability in actual state")
    parser.add_argument("--quota", action="store_true", help="print infos about quota and usage of actual connected mailbox")
    parser.add_argument("--folders", action="store_true", help="print list of available mailbox folders")
    parser.add_argument("--messages", action="store_true", help="print list of messages with size")
    parser.add_argument("--limit", nargs='?', type=int, metavar="foo", help="print a list of message-uid's for mailbox-limiting", const=75)
    # parser.add_argument("--get-info", action="store_true", help="print some infos about the mbman object")
    # parser.add_argument("--get-message", metavar="uid", type=int, help="get message with specific uid from server")
    # parser.add_argument("--autolimit", metavar="percent", type=int, help="limit mailbox to given value", default=80)
    # parser.add_argument("--no-backup", action="store_true", help="must not backup downloaded messages nor use backup")
    args = parser.parse_args()

    try:
        mb = MBMan(args.debug)
        if (args.print_args):
            print(args)
            raise(BaseException)
        if (args.debug >= 4):
            print(args)
        if (args.connect):
            print(mb.connect(server=args.connect))
        if (args.login):
            print(mb.login(user=args.login[0], passwd=args.login[1]))
        if (args.select):
            print(mb.select(mailbox=args.select))
        if (args.examine):
            print(mb.examine(mailbox=args.examine))
        if (args.state):
            print(mb.state())
        if (args.capability):
            print(mb.capability())
        if (args.quota):
            usage, quota = mb.quota()
            print("Usage:", usage, ", Quota:", quota, "(", usage/quota*100, "% )")
        if (args.folders):
            print(mb.folders())
        if (args.messages):
            print(mb.messages())
            # TODO mb.ls sollte die Werte schon parsen
        if (args.limit):
            print(mb.limit_list(lim=args.limit))
    except:
        mb.logout()
        raise
    else:
        mb.logout()
