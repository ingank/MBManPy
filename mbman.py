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
    def __init__(self, debug):
        self.debug = debug
        self.connected = False
        self.authenticated = False
        self.selected = False
        self.logout = False
        self.readonly = True
        self.loop = False
        imaplib.Debug = debug

    def connect(self, server):
        if (self.connected):
            return
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        self.connected = True

    def login(self, user, phrase):
        if (not self.connected):
            return
        if (self.authenticated):
            return
        self.user = user
        self.phrase = phrase
        self.imap4.login(user, phrase)
        self.authenticated = True

    def select(self, mailbox):
        if (not self.connected):
            return
        if (not self.authenticated):
            return
        self.imap4.select(mailbox, readonly=False)
        self.selected = True
        self.readonly = False

    def examine(self, mailbox):
        if (not self.connected):
            return
        if (not self.authenticated):
            return
        self.imap4.select(mailbox, readonly=True)
        self.selected = True
        self.readonly = True

    def disconnect(self):
        if (self.selected):
            self.imap4.close()
            self.selected = False
        if (self.connected):
            self.logout = True
            self.imap4.logout()
            self.authenticated = False
            self.connected = False
            self.logout = False

    def quota(self):
        if (not self.connected):
            return
        if (not self.authenticated):
            return
        quota_root = ('user/' + self.user)
        quota = self.imap4.getquota(quota_root)
        quota, quota = quota
        quota = quota[0].decode("ascii")
        usage, quota = re.findall(r"STORAGE (\d+) (\d+)", quota)[0]
        usage = int(usage)
        quota = int(quota)
        self.usage_val = usage
        self.quota_val = quota
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
