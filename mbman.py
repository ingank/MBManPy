#
# mbman.py
#
# Eine Mailbox Management API in Python.
#
# 2021 by Ingolf Ankert
#

import imaplib
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
        self.state = 'LOGOUT'

    def connect(self, server):
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        self.state = self.imap4.state

    def login(self, user, phrase):
        self.user = user
        self.phrase = phrase
        self.imap4.login(user, phrase)
        self.state = self.imap4.state

    def select(self, mailbox):
        self.imap4.select(mailbox, readonly=False)
        self.state = self.imap4.state

    def examine(self, mailbox):
        self.imap4.select(mailbox, readonly=True)
        self.state = self.imap4.state

    def close(self):
        if (self.state == 'SELECTED'):
            self.imap4.close()
            self.state = self.imap4.state

    def logout(self):
        if (self.state != 'LOGOUT'):
            self.imap4.logout()
            self.state = self.imap4.state

    def disconnect(self):
        self.close()
        self.logout()

    def quota(self):
        quota_root = ('user/' + self.user)
        quota = self.imap4.getquota(quota_root)
        quota, quota = quota
        quota = quota[0].decode("ascii")
        usage, quota = re.findall(r"STORAGE (\d+) (\d+)", quota)[0]
        usage = int(usage)
        quota = int(quota)
        return usage, quota

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
