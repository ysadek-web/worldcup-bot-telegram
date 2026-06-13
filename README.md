# 🏆 World Cup Telegram Bot

Ein mehrsprachiger Telegram-Bot, der Live-Updates zur Fußball-Weltmeisterschaft liefert: Tore, Halbzeit-/Endstände, Gruppentabellen und Spielpläne — automatisch übersetzt in **Deutsch, Englisch, Französisch und Arabisch**, je nach Land/Sprache des Nutzers.

## ✨ Features

- 🌐 Mehrsprachig (DE/EN/FR/AR), automatische Spracheinstellung nach Land
- 🕒 Automatische Zeitzonen-Erkennung pro Land
- ⚽ Live-Updates: Anpfiff, Tore, Halbzeit, Spielende
- 📊 Gruppentabellen auf Abruf oder automatisch nach Spielende
- 📅 Tagesübersicht der heutigen Spiele
- 🔔 Abonnieren/Abbestellen von Updates (`/start`, `/stop`)
- 💾 Persistenter State (überlebt Neustarts)

## 📋 Befehle

| Befehl | Beschreibung |
|---|---|
| `/start` | Bot einrichten (Land/Sprache wählen) |
| `/stop` | Updates abbestellen |
| `/tabelle` | Gruppentabelle anzeigen |
| `/alletabellen` | Alle Gruppentabellen anzeigen |
| `/spiele` | Heutige Spiele anzeigen |
| `/sprache` | Sprache ändern |
| `/land` | Land/Zeitzone ändern |
| `/help` | Hilfe anzeigen |

## 🚀 Setup

### 1. Voraussetzungen

- Python 3.11+
- Ein Telegram-Bot-Token (von [@BotFather](https://t.me/BotFather))
- Ein kostenloser API-Token von [football-data.org](https://www.football-data.org/client/register)

### 2. Installation

```bash
git clone https://github.com/DEIN_USERNAME/worldcup-bot.git
cd worldcup-bot
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Konfiguration

```bash
cp .env.example .env
```

Trage in `.env` deine Tokens ein:

```
TELEGRAM_BOT_TOKEN=dein_telegram_token
FOOTBALL_DATA_TOKEN=dein_football_data_token
```

### 4. Starten

```bash
python main.py
```

## 🐳 Mit Docker

```bash
docker compose up -d --build
```

Die Datei `.env` muss im Projektverzeichnis liegen. Persistente Daten werden in `./data` gespeichert.

## ☁️ Deployment (Railway / Render)

1. Repository auf GitHub pushen
2. Auf [Railway](https://railway.app) oder [Render](https://render.com) ein neues Projekt aus dem GitHub-Repo erstellen
3. Als "Worker"/"Background Service" deployen (kein Webserver nötig)
4. Umgebungsvariablen `TELEGRAM_BOT_TOKEN` und `FOOTBALL_DATA_TOKEN` setzen
5. Start-Command: `python main.py`
6. Persistenten Speicher (Volume) für `/app/data` einrichten, damit `users.json`/`state.json` Neustarts überleben

## 🏗️ Projektstruktur

```
worldcup-bot/
├── bot/
│   ├── config.py          # Konfiguration & Konstanten
│   ├── translations.py    # Mehrsprachige Texte
│   ├── storage.py          # User- & State-Persistenz
│   ├── api_client.py       # Football-Data API
│   ├── telegram_client.py  # Telegram API & Keyboards
│   ├── handlers.py          # Befehls-/Update-Verarbeitung
│   ├── match_tracker.py     # Live-Match-Logik
│   └── logging_config.py    # Logging-Setup
├── tests/                   # Unit-Tests
├── main.py                  # Einstiegspunkt / Main-Loop
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 🧪 Tests

```bash
pip install pytest ruff
pytest
ruff check .
```

## 📄 Lizenz

MIT – siehe [LICENSE](LICENSE)
