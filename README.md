# Mastodon Timeline Filter

Ein Python CLI-Tool zum Filtern von Mastodon-Beiträgen nach Zeiträumen.

## Beschreibung

Dieses Tool ermöglicht es, eigene Mastodon-Beiträge nach bestimmten Zeiträumen zu durchsuchen. Besonders nützlich für das Archivieren von Screenshots, Notizen und anderen Inhalten, die über Mastodon gespeichert werden.

## Voraussetzungen

- Python 3.6+
- `requests` Bibliothek

## Installation

1. Repository klonen oder Skript herunterladen
2. Abhängigkeiten installieren:
   ```bash
   pip install requests
   ```

## Einrichtung

### Access Token erstellen

1. In deiner Mastodon-Instanz: **Einstellungen → Entwicklung**
2. Klicke auf **Neue Anwendung**
3. Name vergeben (z.B. "Timeline Filter")
4. Benötigte Berechtigungen: `read:accounts` und `read:statuses`
5. Speichern und Access Token kopieren

### Credentials konfigurieren

**Option 1: Umgebungsvariablen (empfohlen)**

Füge folgende Zeilen zu `~/.bashrc` oder `~/.zshrc` hinzu:
```bash
export MASTODON_INSTANCE="https://deine-instanz.social"
export MASTODON_TOKEN="dein-access-token"
```

Dann neu laden:
```bash
source ~/.bashrc
```

**Option 2: Parameter beim Aufruf**
```bash
python CLI_Mastodon-Timeline-Filter.py --instance "https://instanz.social" --token "token" --start 01.07.2023 --end 31.07.2023
```

## Verwendung

### Grundlegende Syntax

```bash
python CLI_Mastodon-Timeline-Filter.py --start DATUM --end DATUM [OPTIONEN]
```

### Beispiele

```bash
# Beiträge aus Juli 2023
python CLI_Mastodon-Timeline-Filter.py --start 01.07.2023 --end 31.07.2023

# Mit vollständigem Inhalt
python CLI_Mastodon-Timeline-Filter.py --start 01.07.2023 --end 31.07.2023 --full

# Alternative Datumsformate
python CLI_Mastodon-Timeline-Filter.py --start 2023-07-01 --end 2023-07-31

# Mehrere Accounts: Credentials als Parameter
python CLI_Mastodon-Timeline-Filter.py --instance "https://andere-instanz.social" --token "anderer-token" --start 01.06.2024 --end 30.06.2024
```

### Optionen

| Option | Beschreibung |
|--------|--------------|
| `--start` | Startdatum (DD.MM.YYYY oder YYYY-MM-DD) |
| `--end` | Enddatum (DD.MM.YYYY oder YYYY-MM-DD) |
| `--full` | Zeige vollständigen Beitragsinhalt |
| `--instance` | Mastodon-Instanz URL (überschreibt Umgebungsvariable) |
| `--token` | Access Token (überschreibt Umgebungsvariable) |

### Ausgabe

Das Tool zeigt für jeden gefundenen Beitrag:
- Datum und Uhrzeit
- URL zum Beitrag
- Hashtags
- Medien-Anhänge (mit URLs)
- Beitragsinhalt (gekürzt oder vollständig mit `--full`)

## Hinweise

- Bei vielen Beiträgen kann die Suche einige Zeit dauern
- Die Mastodon API liefert maximal 40 Beiträge pro Request
- Nur eigene Beiträge werden durchsucht, keine Reblogs
- Access Tokens sollten sicher aufbewahrt werden

## Lizenz

GPL-3.0

## Autor

Michael Karbacher