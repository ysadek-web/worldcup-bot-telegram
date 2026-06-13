from typing import Any, Dict, List, Optional
import json

import requests

from bot.config import TELEGRAM_TOKEN, COUNTRIES
from bot.logging_config import get_logger
from bot.storage import get_subscribed_users
from bot.translations import t
from bot.api_client import format_table, get_all_standings

logger = get_logger(__name__)

REQUEST_TIMEOUT = 10
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


# ---------------- Senden ----------------

def send_message_to(chat_id: int, text: str, reply_markup: Optional[Dict[str, Any]] = None) -> None:
    url = f"{TELEGRAM_API}/sendMessage"
    payload: Dict[str, Any] = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        r = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error("Telegram send error (chat %s): %s", chat_id, e)


def broadcast(users: Dict[str, Any], key: str, **kwargs) -> None:
    """Sendet eine übersetzte Nachricht an alle abonnierten Nutzer (jeweils in ihrer Sprache)."""
    for chat_id, u in get_subscribed_users(users).items():
        lang = u.get("lang", "en")
        send_message_to(chat_id, t(key, lang, **kwargs))


def broadcast_table(users: Dict[str, Any], group: Optional[Dict[str, Any]]) -> None:
    """Sendet die Tabelle an alle, jeweils in ihrer Sprache."""
    for chat_id, u in get_subscribed_users(users).items():
        lang = u.get("lang", "en")
        text = format_table(group, lang)
        if text:
            send_message_to(chat_id, text)


# ---------------- Inline Keyboards ----------------

def build_country_keyboard() -> Dict[str, Any]:
    buttons: List[List[Dict[str, str]]] = []
    row: List[Dict[str, str]] = []
    for c in COUNTRIES:
        row.append({"text": c["name"], "callback_data": f"country_{c['code']}"})
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return {"inline_keyboard": buttons}


def build_language_keyboard() -> Dict[str, Any]:
    langs = [
        {"code": "de", "label": "🇩🇪 Deutsch"},
        {"code": "en", "label": "🇬🇧 English"},
        {"code": "fr", "label": "🇫🇷 Français"},
        {"code": "ar", "label": "🇸🇦 العربية"},
    ]
    buttons = [[{"text": lg["label"], "callback_data": f"lang_{lg['code']}"}] for lg in langs]
    return {"inline_keyboard": buttons}


def build_group_keyboard() -> Optional[Dict[str, Any]]:
    standings = get_all_standings()
    if not standings:
        return None
    buttons: List[List[Dict[str, str]]] = []
    row: List[Dict[str, str]] = []
    for group in standings:
        group_name = group.get("group", "")
        letter = group_name.replace("Group ", "")
        row.append({"text": letter, "callback_data": f"table_{group_name}"})
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return {"inline_keyboard": buttons}


def answer_callback_query(callback_id: str) -> None:
    url = f"{TELEGRAM_API}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_id}, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as e:
        logger.error("answerCallbackQuery error: %s", e)


def get_updates(offset: Optional[int]) -> List[Dict[str, Any]]:
    url = f"{TELEGRAM_API}/getUpdates"
    params: Dict[str, Any] = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset + 1
    try:
        r = requests.get(url, params=params, timeout=40)
        r.raise_for_status()
        return r.json().get("result", [])
    except requests.RequestException as e:
        logger.error("getUpdates error: %s", e)
        return []
