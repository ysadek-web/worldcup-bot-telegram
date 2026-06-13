import json
import os
from datetime import timezone
from threading import Lock
from typing import Any, Dict
from zoneinfo import ZoneInfo

from bot.config import USERS_FILE, STATE_FILE
from bot.logging_config import get_logger

logger = get_logger(__name__)

_users_lock = Lock()
_state_lock = Lock()


def _ensure_dir(path: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


# ---------------- User Management ----------------

def load_users() -> Dict[str, Any]:
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Konnte %s nicht laden: %s", USERS_FILE, e)
            return {}
    return {}


def save_users(users: Dict[str, Any]) -> None:
    _ensure_dir(USERS_FILE)
    tmp_file = f"{USERS_FILE}.tmp"
    with _users_lock:
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            os.replace(tmp_file, USERS_FILE)
        except OSError as e:
            logger.error("Konnte %s nicht speichern: %s", USERS_FILE, e)


def get_user(users: Dict[str, Any], chat_id: int):
    return users.get(str(chat_id))


def get_lang(users: Dict[str, Any], chat_id: int) -> str:
    u = get_user(users, chat_id)
    return u["lang"] if u else "en"


def get_tz(users: Dict[str, Any], chat_id: int):
    u = get_user(users, chat_id)
    if u and u.get("tz"):
        try:
            return ZoneInfo(u["tz"])
        except Exception:
            return timezone.utc
    return timezone.utc


def get_subscribed_users(users: Dict[str, Any]) -> Dict[int, Any]:
    return {int(cid): u for cid, u in users.items() if u.get("subscribed")}


# ---------------- Bot State (persistente Sets/Dicts) ----------------

DEFAULT_STATE = {
    "sent_start": [],
    "sent_halftime": [],
    "sent_finish": [],
    "table_sent": [],
    "last_score": {},      # match_id (str) -> [gh, ga]
    "last_update_id": None,
}


def load_state() -> Dict[str, Any]:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_STATE.copy()
                merged.update(data)
                return merged
        except (json.JSONDecodeError, OSError) as e:
            logger.error("Konnte %s nicht laden: %s", STATE_FILE, e)
    return DEFAULT_STATE.copy()


def save_state(state: Dict[str, Any]) -> None:
    _ensure_dir(STATE_FILE)
    tmp_file = f"{STATE_FILE}.tmp"
    with _state_lock:
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            os.replace(tmp_file, STATE_FILE)
        except OSError as e:
            logger.error("Konnte %s nicht speichern: %s", STATE_FILE, e)
