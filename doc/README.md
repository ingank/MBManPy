# MBManPy/doc
Dokumentation des Projektes MBManPy.

## Ausgangslage
Heutige IMAP-Clients,
beispielsweise Mozilla Thunderbird,
sind in erster Linie für den Abruf
elektronischer Nachrichten von IMAP-Konten
sowie deren grafische Darstellung auf einem Bildschirm optimiert.
Augenmerk wird vor allem auf die Benutzerfreundlichkeit und Schnelligkeit gelegt;
oft zu Lasten:
* der Datenintegrität
* der Nutzung von menschenlesbaren lokalen Speicherformaten
* der Transparenz von Client-Server-Interaktionen
* der automatisierten Durchführung von Wartungsarbeiten

## Aufgabenstellung
Ausbaustufe 1:
* SSL-Verbindung zu einem IMAP-Server aufbauen
* Verbindung zum IMAP-Server in jedem Betriebszustand kontrolliert abbauen
* Per User/Password an einem IMAP-Konto anmelden
* Postfachtopographie ermitteln (Unterordner)
* Nachrichten vom IMAP-Konto herunterladen
* Automatisches Backup von heruntergeladenen Nachrichten im Format `.eml`
* Nachrichten auf dem Server gezielt löschen
* Automatisiert Freiraum in knapp bemessenen Postfächern schaffen (Limiter)
* Protokoll über die ausgeführten Tätigkeiten führen
* Auf neue Nachrichten warten und Folgeaktionen triggern (IDLE)
* IMAP-Metadaten bereitstellen
* Transcodierung von Nachrichten und Headerdaten breitstellen

Ausbaustufe 2:
* Nachrichten innerhalb des IMAP-Kontos verschieben
* Nachrichten auf das IMAP-Konto hochladen
* Lokale Datenbank als Datenquelle nutzen
* IMAP-Datensätze lokal generieren
  * Mischungen aus mehreren IMAP-Konten
  * Filter anwenden
* IMAP-Datensätze auf IMAP-Konten hochladen
  * nur fehlende Nachrichten
  * Komplettbackup (vorheriges WIPE)
* Named Pipe für den direkten Zugriff auf MBManPy-Befehle

## Datenorte, Formate, Abhängigkeiten
Lokale Datenbank der Nachrichtenbackups:
* Standard-Dateiname: `~/MBData/IMAP-USER/POSTFACH/UIDVALIDITY-UID8DIGIT.eml`
* Dateiformat: `.eml` (ASCII-Text)
* Stammordner `~/MBData/` kann geändert werden
* Jede komplett heruntergeladene Nachricht wird automatisch gesichert
* Jede lokal vorhandene Nachricht wird der entfernten vorgezogen
* Möglichkeit, lokal fehlende Nachrichten explizit zu laden
* Möglichkeit, ein komplettes Backup zu forcieren

Nachrichtenmetadaten:
* MIME zu Unicode transcodieren
* Adressaten uniformieren (definiertes Adressformat)
* Zeitangaben uniformieren (definiertes Zeitformat)
* Headerdaten parsen

IMAP-Metadaten:
* Quota
* UID Validity
* Capabilities

Schnittstellendaten:
* Terminal OUT
  * ASCII-Text
  * Unicode-Text
  * Inhalte von Variablen und Strukturen
* Terminal IN
  * Argumente als Unicode-Text
* IMAP4 (imaplib)
  * UID's als ASCII-Text:
    * seq-number
    * seq-range
    * sequence-set
* Intern
  * RAW Byte Code
  * ASCII - Text
