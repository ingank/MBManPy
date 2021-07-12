# FAQ

__Frage 1:__ Warum das Rad neu erfinden, wo es doch das Modul `imaplib` und die Bibliothek `imapclient` gibt?

__Antwort 1:__ Das Projekt MBManPy nutzt extensiv die Funktionalitäten der Bibliothek `imapclient`. Gleichzeitig stutzt es dessen Funktionsumfang genau auf das Maß, um ein automatisiertes Management von IMAP-Konten transparent und ausfallsicher gestalten zu können. Es wird ein besonderes Augenmerk darauf gerichtet, Ausnahmen so zu behandeln, dass der Regelbetrieb nach einem Verbindungsabbruch oder sonstigen Fehlern automatisch wieder aufgenommen wird.
