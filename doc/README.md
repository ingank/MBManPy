# MBManPy/doc
Dokumentation des Projektes MBManPy

## Aufgabenstellung
Dem Benutzer werden Werkzeuge bereitgestellt,
die wiederkehrende Wartungsarbeiten an IMAP-Benutzerkonten
automatisch erledigen.

## Teilaufgaben und deren Aspekte

### Version 1
* Adressierung von Nachrichten mittels UID-Sequence-Set
* Nachrichten vom IMAP-Konto herunterladen
* Nachrichten entfernt löschen
  * konkret
  * automatisiert
* Nachrichten in einer lokalen Datenbank speichern
  * nur heruntergeladene Nachrichten (Cache)
  * nur fehlende Nachrichten
  * Komplettbackup
* Nachrichtenmetadaten aufbereiten
  * MIME zu Unicode
  * Adressaten uniformieren
  * Headerdaten parsen
* IMAP-Metadaten bereitstellen und verwerten
  * Quota
  * UID Validity
  * Capabilities
* Datenaufbereitung
  * Terminal
    * ASCII - Text
    * Unicode - Text
    * RAW - Text
  * IMAP4 (imaplib)
    * UID's (ASCII-Text)
      * seq-number
      * seq-range
      * sequence-set
  * Intern
    * RAW Byte Code
    * ASCII - Text
  * Nachrichtendateien
    * EML - Format
    * ASCII - Text
  * API (Argumente)

### Version 2
* Nachrichten innerhalb des IMAP-Kontos verschieben
* Nachrichten auf das IMAP-Konto hochladen
* Lokale Datenbank als Datenquelle zu nutzen
* IMAP-Datensätze lokal generieren
  * Mischungen aus mehreren IMAP-Konten
  * Filter anwenden
* IMAP-Datensätze auf IMAP-Konten hochladen
  * nur fehlende Nachrichten
  * Komplettbackup (vorheriges WIPE)
