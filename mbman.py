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
        self.debug = debug
        self.server = None
        self.user = None
        self.passwd = None
        self.db_root = os.environ['HOME'] + '/MBData/'
        self.db_uidlength = 8
        self.mb_selected = None
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

    def select(self, mailbox='INBOX', readonly=True):
        ok, response = self.imap4.select(mailbox, readonly)
        self.mb_flags = self.imap4.response('FLAGS')[1]
        self.mb_exists = self.imap4.response('EXISTS')[1]
        self.mb_recent = self.imap4.response('RECENT')[1]
        self.mb_uidvalidity = self.imap4.response('UIDVALIDITY')[1]
        self.mb_uidnext = self.imap4.response('UIDNEXT')[1]
        self.mb_selected = mailbox
        return ok, response

    def close(self):
        ok = b'NO'
        response = b'Not in Selected State'
        if self.state() == 'SELECTED':
            ok, response = self.imap4.close()
            self.mb_flags = None
            self.mb_exists = None
            self.mb_recent = None
            self.mb_uidvalidity = None
            self.mb_uidnext = None
            self.mb_selected = None
        return ok, response

    def logout(self):
        self.close()
        return self.imap4.logout()

    def quota(self):
        quota_root = ('user/' + self.user)
        quota = self.imap4.getquota(quota_root)
        quota, quota = quota
        quota = quota[0].decode("ascii")
        usage, quota = re.findall(r"STORAGE (\d+) (\d+)", quota)[0]
        usage = int(usage) * 1024
        quota = int(quota) * 1024
        return usage, quota

    def boxes(self):
        ok, response = self.imap4.list()
        if (ok == 'OK'):
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
        else:
            return False

    def ls(self):
        return self.imap4.uid('fetch', '0:*', "RFC822.SIZE")

    def ls_al(self):
        return self.imap4.uid('fetch', '0:*', "ALL")

    def limit(self, lim=75):
        #
        # Gibt eine Liste mit UID's zurück,
        # die nach der Löschung der entsprechenden Nachrichten auf dem Server
        # den genutzten Speicher genau unterhalb der limitierten Größe des
        # IMAP-Accounts (Quota) einmessen würde.
        #
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

    def message_fetch(self, uid: str, delete=False):
        """
        Eine Nachricht von der aktuellen Mailbox laden

        Args:
            uid (str): UID der Nachricht
            delete (bool, optional): Nachricht auf dem Server löschen?. Defaults to False.

        Returns:
            (byte): geladene Nachricht
        """
        mailbox = 'INBOX'
        ok, response = self.select(mailbox, readonly=not(delete))
        ok, response = self.imap4.uid('fetch', uid, "RFC822")
        message = response[0][1]
        if delete:
            # Nachricht wird vorerst NICHT als `\Deleted` markiert
            # self.imap4.uid('store', uid, '+FLAGS', '\\Deleted')
            self.imap4.uid('store', uid, '-FLAGS', '\\Deleted')
        return ok, message

    def db_path(self):
        #
        # Erzeuge den Pfad auf die lokale Backup-Datenbank
        # für den aktuellen IMAP-Account und innerhalb dessen
        # auf die aktuelle Mailbox, wenn er noch nicht vorhanden ist.
        # Gib in jedem Fall die Pfadangabe zurück.
        # Voraussetzung ist der 'SELECTED' State.
        #
        if self.mb_selected:
            path = self.db_root
            path = path + self.user + '/'
            path = path + self.mb_selected + '/'
            path = path + self.mb_uidvalidity[0].decode('ascii') + '/'
            if not os.path.exists(path):
                os.makedirs(path)
            return path
        else:
            return None

    def db_save(self, uid, mailbox='INBOX', readonly=True):
        dummy, response = self.select(mailbox, readonly)
        path = db_path() + 'test.txt'
        f = open(path, "w")
        f.write("Woops! I have deleted the content!")
        f.close()

    #
    # TESTING AREA!!!
    #

    # idle, idle_done:
    # Copyright (c) 2012 Mathieu Lecarme
    # This code is licensed under the MIT license

    def idle(self):
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

    def idle_done(self):
        connection = self.imap4
        connection.send(b'DONE\r\n')
        connection.readline()
        self.loop = False
