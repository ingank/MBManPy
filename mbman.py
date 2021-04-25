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

    def __init__(self, debug):
        imaplib.Debug = debug

    def state(self):
        return self.imap4.state

    def state_is(self, value):
        return (self.imap4.state == value)

    def capability(self):
        return self.imap4.capability()

    def connect(self, server):
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        return True

    def login(self, user, phrase):
        self.user = user
        self.phrase = phrase
        return self.imap4.login(user, phrase)

    def select(self, mailbox):
        return self.imap4.select(mailbox, readonly=False)

    def examine(self, mailbox):
        return self.imap4.select(mailbox, readonly=True)

    def close(self):
        if self.state_is('SELECTED'):
            return(self.imap4.close())
        else:
            return False

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

    def folder(self):
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

    def limit(self, lim=75, mailbox='INBOX'):
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
        ok, response = self.examine(mailbox)
        ok, response = self.ls()
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

    def message_fetch(self, uid, mailbox='INBOX'):
        #
        # Gibt die Nachricht als Text zurück,
        # die mit Hilfe von `uid` und `mailbox` adressiert wird.
        # Die Nachricht verbleibt auf dem Server.
        #
        ok, response = self.examine(mailbox)
        ok, response = self.imap4.uid('fetch', uid, "RFC822")
        response = response[0][1].decode("ascii")
        return response

    def message_cut(self, uid, mailbox='INBOX'):
        #
        # Gibt die Nachricht als Text zurück,
        # die mit Hilfe von `uid` und `mailbox` adressiert wird.
        # Die Nachricht wird zum Löschen vorgemerkt.
        #
        ok, response = self.select(mailbox)
        ok, response = self.imap4.uid('fetch', uid, "RFC822")
        message = response[0][1].decode("ascii")
        # Nachricht wird vorerst NICHT als `\Deleted` markiert
        # ok, response = self.imap4.uid('store', uid, '+FLAGS', '\\Deleted')
        ok, response = self.imap4.uid('store', uid, '-FLAGS', '\\Deleted')
        return message

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
