#
# mbman.py
#
# Eine Mailbox Management API in Python.
#
# 2021 by Ingolf Ankert
#

import imaplib


class MBMan:
    def __init__(self, debug):
        self.debug = debug
        self.connected = False
        self.opened = False
        imaplib.Debug = debug

    def connect(self, server):
        if (self.connected):
            return
        if (self.opened):
            return
        self.server = server
        self.imap4 = imaplib.IMAP4_SSL(server)
        self.connected = True

    def login(self, user, phrase):
        if (not self.connected):
            return
        if (self.opened):
            return
        self.user = user
        self.phrase = phrase
        self.imap4.login(user, phrase)
        self.opened = True

    def disconnect(self):
        if (self.opened):
            self.imap4.close()
            self.opened = False
        if (self.connected):
            self.imap4.logout()
            self.connected = False
