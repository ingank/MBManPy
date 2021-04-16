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
