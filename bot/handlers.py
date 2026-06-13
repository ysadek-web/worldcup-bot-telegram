from typing import Any, Dict, List, Optional

from bot.config import COUNTRIES
from bot.logging_config import get_logger
from bot.storage import get_lang, get_tz, save_users
from bot.translations import t
from bot.api_client import (
    get_standings_by_group,
    get_all_standings,
    format_table,
    format_today_matches,
)
from bot.telegram_client import (
    send_message_to,
    answer_callback_query,
    build_country_keyboard,
    build_language_keyboard,
    build_group_keyboard,
)

logger = get_logger(__name__)


def handle_callback_query(cq: Dict[str, Any], users: Dict[str, Any]) -> None:
    chat_id = cq["message"]["chat"]["id"]
    data_str = cq.get("data", "")
    cid_key = str(chat_id)

    if data_str.startswith("country_"):
        code = data_str.replace("country_", "")
        country = next((c for c in COUNTRIES if c["code"] == code), None)
        if country:
            users.setdefault(cid_key, {})
            users[cid_key]["country"] = country["name"]
            users[cid_key]["tz"] = country["tz"]
            users[cid_key]["lang"] = country["lang"]
            users[cid_key]["subscribed"] = True
            save_users(users)
            lang = country["lang"]
            send_message_to(chat_id, t("setup_done", lang, country=country["name"], tz=country["tz"]))
            send_message_to(chat_id, t("help", lang))

    elif data_str.startswith("lang_"):
        lang = data_str.replace("lang_", "")
        users.setdefault(cid_key, {})
        users[cid_key]["lang"] = lang
        users[cid_key].setdefault("subscribed", True)
        users[cid_key].setdefault("tz", "UTC")
        save_users(users)
        send_message_to(chat_id, t("lang_set", lang))

    elif data_str.startswith("table_"):
        group_name = data_str.replace("table_", "")
        lang = get_lang(users, chat_id)
        group = get_standings_by_group(group_name)
        table_text = format_table(group, lang)
        send_message_to(chat_id, table_text or t("no_table", lang))

    answer_callback_query(cq["id"])


def handle_command(chat_id: int, cmd: str, users: Dict[str, Any]) -> None:
    cid_key = str(chat_id)
    lang = get_lang(users, chat_id)

    if cmd == "/start":
        send_message_to(chat_id, t("welcome", lang), reply_markup=build_country_keyboard())

    elif cmd == "/stop":
        if cid_key in users:
            users[cid_key]["subscribed"] = False
            save_users(users)
        send_message_to(chat_id, t("unsubscribed", lang))

    elif cmd == "/help":
        send_message_to(chat_id, t("help", lang))

    elif cmd == "/sprache":
        send_message_to(chat_id, t("choose_lang", lang), reply_markup=build_language_keyboard())

    elif cmd == "/land":
        send_message_to(chat_id, t("welcome", lang), reply_markup=build_country_keyboard())

    elif cmd == "/tabelle":
        keyboard = build_group_keyboard()
        if keyboard:
            send_message_to(chat_id, t("choose_group", lang), reply_markup=keyboard)
        else:
            send_message_to(chat_id, t("no_table", lang))

    elif cmd == "/alletabellen":
        standings = get_all_standings()
        if not standings:
            send_message_to(chat_id, t("no_table", lang))
        else:
            for group in standings:
                text_table = format_table(group, lang)
                if text_table:
                    send_message_to(chat_id, text_table)

    elif cmd == "/spiele":
        tz = get_tz(users, chat_id)
        send_message_to(chat_id, format_today_matches(lang, tz))

    elif cmd.startswith("/"):
        send_message_to(chat_id, t("unknown_cmd", lang) + "\n\n" + t("help", lang))


def process_updates(updates: List[Dict[str, Any]], users: Dict[str, Any]) -> Optional[int]:
    """Verarbeitet eine Liste von Telegram-Updates.
    Gibt die letzte update_id zurück (oder None, falls keine Updates)."""
    last_update_id: Optional[int] = None

    for update in updates:
        last_update_id = update["update_id"]

        if "callback_query" in update:
            try:
                handle_callback_query(update["callback_query"], users)
            except Exception as e:
                logger.exception("Fehler bei callback_query: %s", e)
            continue

        message = update.get("message", {})
        text = message.get("text", "").strip()
        chat_id = message.get("chat", {}).get("id")

        if chat_id is None or not text:
            continue

        try:
            handle_command(chat_id, text.lower(), users)
        except Exception as e:
            logger.exception("Fehler bei Befehl '%s' von chat %s: %s", text, chat_id, e)

    return last_update_id
