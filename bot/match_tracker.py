from typing import Any, Dict

from bot.logging_config import get_logger
from bot.storage import get_subscribed_users
from bot.translations import t
from bot.api_client import get_match_info, get_standings_by_group
from bot.telegram_client import send_message_to, broadcast, broadcast_table

logger = get_logger(__name__)


def process_match(match: Dict[str, Any], users: Dict[str, Any], state: Dict[str, Any]) -> bool:
    """Verarbeitet ein einzelnes Match und aktualisiert `state` in-place.
    Gibt True zurück, falls sich der State verändert hat (-> speichern)."""
    match_id = str(match["id"])
    status = match["status"]
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]

    score = match.get("score", {})
    full_time = score.get("fullTime", {})
    half_time = score.get("halfTime", {})

    gh_full = full_time.get("home")
    ga_full = full_time.get("away")
    gh_half = half_time.get("home")
    ga_half = half_time.get("away")

    changed = False

    sent_start = set(state["sent_start"])
    sent_halftime = set(state["sent_halftime"])
    sent_finish = set(state["sent_finish"])
    table_sent = set(state["table_sent"])
    last_score = state["last_score"]

    # Spielstart mit erweiterten Infos
    if status in ("IN_PLAY", "PAUSED") and match_id not in sent_start:
        venue, stage_display, referee_name = get_match_info(match)
        for chat_id, u in get_subscribed_users(users).items():
            lang = u.get("lang", "en")
            referee_text = referee_name if referee_name else t("unknown", lang)
            send_message_to(chat_id, t(
                "start_match", lang,
                home=home, away=away,
                venue=venue, stage=stage_display, referee=referee_text
            ))
        sent_start.add(match_id)
        changed = True
        if gh_full is not None and ga_full is not None:
            last_score[match_id] = [gh_full, ga_full]

    # Tor-Erkennung (nur Score-Vergleich, ohne Torschütze)
    if status in ("IN_PLAY", "PAUSED", "FINISHED"):
        if gh_full is not None and ga_full is not None:
            current_score = [gh_full, ga_full]
            prev_score = last_score.get(match_id)
            if prev_score is not None and current_score != prev_score:
                broadcast(users, "goal", home=home, away=away, gh=gh_full, ga=ga_full)
            if prev_score != current_score:
                last_score[match_id] = current_score
                changed = True

    # Halbzeit
    if status == "PAUSED" and match_id not in sent_halftime and gh_half is not None:
        broadcast(users, "halftime", home=home, away=away, gh=gh_half, ga=ga_half)
        sent_halftime.add(match_id)
        changed = True

    # Spielende + Tabelle
    if status == "FINISHED" and match_id not in sent_finish:
        gh = gh_full if gh_full is not None else 0
        ga = ga_full if ga_full is not None else 0
        broadcast(users, "finish", home=home, away=away, gh=gh, ga=ga)
        sent_finish.add(match_id)
        changed = True

        group_field = match.get("group")
        if group_field and match_id not in table_sent:
            group = get_standings_by_group(group_field)
            broadcast_table(users, group)
            table_sent.add(match_id)

    if changed:
        state["sent_start"] = list(sent_start)
        state["sent_halftime"] = list(sent_halftime)
        state["sent_finish"] = list(sent_finish)
        state["table_sent"] = list(table_sent)

    return changed
