# MBManPy

Portierung des Projektes MBMan in Python.

## Installation
```
git clone git@github.com:ingank/MBManPy.git
```

## IMAP4

### Zustand der Verbindung (State of connection)

Es gibt vier Zustände einer IMAP4 Client-Server-Verbindung.

* __Nicht authentifizierter Zustand (Not Authenticated State)__
  * Konkretisiert den Zustand vom Beginn des _Server Greeting_ bis zum Abschluss der Benutzeranmeldung.
  * Mögliche IMAP-Befehle (Capabilities):
    * AUTHENTICATE
    * CAPABILITY
    * LOGIN
    * LOGOUT
    * NOOP
    * STARTTLS
* __Authentifizierter Zustand (Authenticated State)__
  * Der Nutzer konnte sich gegenüber dem IMAP-Server authentifizieren.
  * Der _Authenticated State_ kann herbeigeführt werden mit den Befehlen:
    * `AUTHENTICATE`
    * `LOGIN`
  * Mögliche IMAP-Befehle (Capabilities):
    * Alle Befehle des _Not Authenticated State_
    * SELECT
    * EXAMINE
    * CREATE
    * DELETE
    * RENAME
    * SUBSCRIBE
    * UNSUBSCRIBE
    * LIST
    * LSUB
    * STATUS
    * APPEND
* __Ausgewählter Zustand (Selected State)__
  * Ein bestimmtes Postfach wurde ausgewählt.
  * Der _Selected State_ kann herbeigeführt werden mit den Befehlen:
    * `SELECT`: Lese-/schreibzugriff auf die Mailbox.
    * `EXAMINE`: Lesezugriff auf die Mailbox.
  * Mögliche IMAP-Befehle (Capabilities):
    * Alle Befehle des _Not Authenticated State_
    * Alle Befehle des _Authenticated State_
    * CHECK
    * CLOSE
    * EXPUNGE
    * SEARCH
    * FETCH
    * STORE
    * COPY
    * UID
* __Abmeldezustand (Logout State)__
  * konkretisiert den Zustand zwischen dem Senden des Befehls `LOGOUT` und der Serverantwort `BYE`
  * Mögliche IMAP-Befehle (Capabilities):
    * CAPABILITY
    * LOGOUT
    * NOOP

### Zusammenfassung

|COMMAND|NONAUTH|AUTH|SELECTED|LOGOUT|OBSOLET|
|-|:-:|:-:|:-:|:-:|:-:|
|APPEND| |X|X| | |
|AUTHENTICATE|X| | | | |
|CAPABILITY|X|X|X|X| |
|CHECK| | |X| | |
|CLOSE| | |X| | |
|COPY| | |X| | |
|CREATE| |X|X| | |
|DELETE| |X|X| | |
|DELETEACL| |X|X| | |
|ENABLE| |X| | |  |
|EXAMINE| |X|X| | |
|EXPUNGE| | |X| | |
|FETCH| | |X| | |
|GETACL| |X|X| | |
|GETANNOTATION| |X|X| | |
|GETQUOTA| |X|X| | |
|GETQUOTAROOT| |X|X| | |
|MYRIGHTS| |X|X| | |
|LIST| |X|X| | |
|LOGIN|X| | | | |
|LOGOUT|X|X|X|X| |
|LSUB| |X|X| | |
|MOVE| | |X| | |
|NAMESPACE| |X|X| | |
|NOOP|X|X|X|X| |
|PARTIAL| | |X| |X|
|PROXYAUTH| |X| | | |
|RENAME| |X|X| | |
|SEARCH| | |X| | |
|SELECT| |X|X| | |
|SETACL| |X|X| | |
|SETANNOTATION| |X|X| | |
|SETQUOTA| |X|X| | |
|SORT| | |X| | |
|STARTTLS|X| | | | |
|STATUS| |X|X| | |
|STORE| | |X| | |
|SUBSCRIBE| |X|X| | |
|THREAD| | |X| | |
|UID| | |X| | |
|UNSUBSCRIBE| |X|X| | |