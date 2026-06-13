import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
FD_TOKEN = os.environ["FOOTBALL_DATA_TOKEN"]

API_HOST = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": FD_TOKEN}

WC_COMPETITION = "WC"
POLL_INTERVAL = 30

USERS_FILE = os.environ.get("USERS_FILE", "data/users.json")
STATE_FILE = os.environ.get("STATE_FILE", "data/state.json")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# ---------------- Länder / Zeitzonen ----------------

COUNTRIES = [
    {"code": "DE", "name": "Deutschland", "tz": "Europe/Berlin", "lang": "de"},
    {"code": "FR", "name": "France", "tz": "Europe/Paris", "lang": "fr"},
    {"code": "GB", "name": "United Kingdom", "tz": "Europe/London", "lang": "en"},
    {"code": "US", "name": "USA", "tz": "America/New_York", "lang": "en"},
    {"code": "MA", "name": "المغرب", "tz": "Africa/Casablanca", "lang": "ar"},
    {"code": "EG", "name": "مصر", "tz": "Africa/Cairo", "lang": "ar"},
    {"code": "SA", "name": "السعودية", "tz": "Asia/Riyadh", "lang": "ar"},
    {"code": "TN", "name": "تونس", "tz": "Africa/Tunis", "lang": "ar"},
    {"code": "QA", "name": "قطر", "tz": "Asia/Qatar", "lang": "ar"},
    {"code": "BE", "name": "Belgique", "tz": "Europe/Brussels", "lang": "fr"},
    {"code": "CH", "name": "Schweiz/Suisse", "tz": "Europe/Zurich", "lang": "de"},
    {"code": "ES", "name": "España", "tz": "Europe/Madrid", "lang": "en"},
]
