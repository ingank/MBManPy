#
# mbman.py
#
# Eine Mailbox Management API in Python.
#
# 2021 by Ingolf Ankert
#

import imaplib
import email
import os
import re


class MBMan:

    special_use = (
        # RFC 6154
        # IETF Draft: IMAP LIST extension for special-use mailboxes
        'All',
        'Archive',
        'Drafts',
        'Flagged',
        'Junk',
        'Sent',
        'Trash',
        'AllMail',  # obsolete
        'Spam',    # obsolete
        'Starred'  # obsolete
    )

    def __init__(self, debug=0):
        imaplib.Debug = debug
        self.imap4 = None
        self.debug = debug
        self.server = None
        self.user = None
        self.passwd = None
        self.last_message = None
        self.last_message_path = None
        self.last_uid = None
        self.db_root = os.environ['HOME'] + '/MBData/'
        self.db_uidlength = 8
        self.db_path = None
        self.db_file = None
        self.db_autosave = None
        self.mb_selected = None
        self.mb_readonly = None
        self.mb_uidvalidity = None
        self.mb_uidnext = None
        self.mb_flags = None
        self.mb_exists = None
        self.mb_recent = None

    def state(self):
        return self.imap4.state

    def capability(self):
        return self.imap4.capability()

    def connect(self, server):
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        return True

    def login(self, user, passwd):
        self.user = user
        self.passwd = passwd
        return self.imap4.login(user, passwd)

    def select(self, mailbox='INBOX', readonly=True, autosave=True):
        """Eine Mailbox anwählen.

        Args:
            mailbox (str, optional): Name der Mailbox. Defaults to 'INBOX'.
            readonly (bool, optional): Schreibgeschützt öffnen? Defaults to True.

        Returns:
            (typ,[data]): typ = Result, data = Response
        """
        typ, data = self.imap4.select(mailbox, readonly)
        self.mb_flags = self.imap4.response('FLAGS')[1]
        self.mb_exists = self.imap4.response('EXISTS')[1]
        self.mb_recent = self.imap4.response('RECENT')[1]
        self.mb_uidvalidity = self.imap4.response('UIDVALIDITY')[1]
        self.mb_uidnext = self.imap4.response('UIDNEXT')[1]
        self.mb_selected = mailbox
        self.mb_readonly = readonly
        self.db_autosave = autosave
        if autosave:
            path = self.db_root
            path += self.user + '/'
            path += mailbox + '/'
            if not os.path.exists(path):
                os.makedirs(path)
            self.db_path = path
        return typ, data

    def close(self):
        if not self.mb_selected:
            return None
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
        if not self.imap4:
            return None
        typ, data = self.close()
        typ, data = self.imap4.logout()
        self.server = None
        self.user = None
        self.passwd = None
        self.imap4 = None
        return typ, data

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

    def quota(self):
        quota_root = ('user/' + self.user)
        quota = self.imap4.getquota(quota_root)
        quota, quota = quota
        quota = quota[0].decode("ascii")
        usage, quota = re.findall(r"STORAGE (\d+) (\d+)", quota)[0]
        usage = int(usage) * 1024
        quota = int(quota) * 1024
        return usage, quota

    def folders(self):
        ok, response = self.imap4.list()
        if not (ok == 'OK'):
            return None
        folders = []
        for line in response:
            line = line.decode("ascii")
            line = re.split(' "." ', line)
            line = (
                re.findall(r"^\((.*)\)$", line[0])[0],
                re.findall(r"^\"(.*)\"$", line[1])[0]
            )
            special = 'NoSpecial'
            for su in self.special_use:
                if (line[0].find(su) != -1):
                    special = su
                    break
            folders.append([special, line[1]])
        return folders

    def ls(self):
        return self.imap4.uid('fetch', '0:*', "RFC822.SIZE")

    def ls_al(self):
        return self.imap4.uid('fetch', '0:*', "ALL")

    def limit(self, lim=75):
        """
        Gibt eine Liste mit UID's zurück,
        die nach der Löschung der entsprechenden Nachrichten auf dem Server
        den genutzten Speicher genau unterhalb der limitierten Größe des
        MAP-Accounts (Quota) einmessen würde.

        Args:
            lim (int, optional): Der Limit-Wert in Prozent. Defaults to 75.

        Returns:
            ([uid:str, ...]): Liste von UID's oder leere Liste
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
        """
        Eine Nachricht von der aktuellen Mailbox laden.

        Wenn Mailbox nicht `readonly` selektiert wurde,
        dann wird die Nachricht als gelöscht markiert.

        Eine Kopie wird unter self.last_message gespeichert.

        Args:
            uid (str): UID der Nachricht

        Returns:
            (str): geladene Nachricht
        """
        dummy, response = self.imap4.uid('fetch', uid, "RFC822")
        message = response[0][1].decode('ascii')
        self.last_message = message
        self.last_uid = uid
        if not self.mb_readonly:
            pass
            self.imap4.uid('store', uid, '+FLAGS', '\\Deleted')
        if self.db_autosave:
            uid_val = self.mb_uidvalidity[0].decode('ascii')
            length = len(uid)
            null_count = self.db_uidlength - length
            file_path = self.db_path
            file_path += uid_val + '_'
            file_path += '0' * null_count + uid
            file_path += '.eml'
            self.message_save(message, file_path)
            self.db_file = file_path
        return message

    def message_save(self, message: str, path: str):
        """
        Speichert eine Nachricht in einer Datei.

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


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description='A Python program using modul mbman.py')
    # Optionen
    parser.add_argument("-x", "--expunge", action="store_true", help="delete messages on server")
    parser.add_argument("-c", "--check-validity", action="store_true", help="check backup-files against server-data")
    parser.add_argument("-a", "--print-args", action="store_true", help="print parsed command line arguments")
    # Parameter
    parser.add_argument("-s", "--server", metavar="foo", help="given server name")
    parser.add_argument("-u", "--user", metavar="foo", help="given username")
    parser.add_argument("-p", "--passwd", metavar="foo", help="given password")
    parser.add_argument("-m", "--folder", metavar="foo", help="select a mailbox folder")
    parser.add_argument("-l", "--limit", metavar="int", type=int, help="set limit to int percent")
    parser.add_argument("-i", "--uid", metavar="int", type=int, help="select message with uid int")
    parser.add_argument("-d", "--debug", metavar="int", type=int, help="set debug level to int", default=0)
    # Befehle
#    parser.add_argument("--connect", action="store_true", help="connect to imap server")
#    parser.add_argument("--login", action="store_true", help="login to an imap user account")
    parser.add_argument("--get-quota", action="store_true", help="print infos about quota and usage")
    parser.add_argument("--get-folders", action="store_true", help="print a list of available mailbox folders")
    parser.add_argument("--get-info", action="store_true", help="print some infos about the mbman object")
    parser.add_argument("--get-message", action="store_true", help="get a message from server")
    parser.add_argument("--select", action="store_true", help="select a specific mailbox (use with parameter '-m'")
    parser.add_argument("--examine", action="store_true", help="select a specific mailbox readonly")
    parser.add_argument("--autolimit", action="store_true", help="automatic limit and backup the mailbox")
    #-#
    args = parser.parse_args()
    mb = MBMan(args.debug)
    try:
        if (args.print_args):
            print(args)
        if (args.server):
            print(mb.connect(server=args.server))
        if (args.user and args.passwd):
            print(mb.login(user=args.user, passwd=args.passwd))
        if (args.get_quota):
            usage, quota = mb.quota()
            print(usage, quota, " = ", usage/quota*100, "%")
        if (args.get_folders):
            print(mb.folders())
        if (args.folder):
            if (args.select):
                print(mb.select(args.folder, readonly=False))
            if (args.examine):
                print(mb.select(args.folder, readonly=True))
    except:
        mb.logout()
        raise
    else:
        mb.logout()
