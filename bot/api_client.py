from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

import requests

from bot.config import API_HOST, HEADERS, WC_COMPETITION
from bot.logging_config import get_logger
from bot.translations import t

logger = get_logger(__name__)

REQUEST_TIMEOUT = 30


def get_today_matches() -> List[Dict[str, Any]]:
    today = date.today().isoformat()
    url = f"{API_HOST}/competitions/{WC_COMPETITION}/matches"
    params = {"dateFrom": today, "dateTo": today}
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json().get("matches", [])
    except requests.RequestException as e:
        logger.error("API error (matches): %s", e)
        return []


def get_all_standings() -> List[Dict[str, Any]]:
    url = f"{API_HOST}/competitions/{WC_COMPETITION}/standings"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json().get("standings", [])
    except requests.RequestException as e:
        logger.error("API error (standings): %s", e)
        return []


def get_standings_by_group(group_name: str) -> Optional[Dict[str, Any]]:
    for group in get_all_standings():
        if group.get("group", "") == group_name:
            return group
    return None


def format_table(group: Optional[Dict[str, Any]], lang: str) -> Optional[str]:
    if not group:
        return None
    group_name = group.get("group", "Gruppe")
    header = t("table_header", lang, group=group_name)
    points_label = t("points", lang)
    lines = [header]
    medals = ["🥇", "🥈", "🥉", "4️⃣"]
    for i, entry in enumerate(group.get("table", [])):
        name = entry["team"]["name"]
        points = entry["points"]
        played = entry.get("playedGames", 0)
        prefix = medals[i] if i < len(medals) else f"{i + 1}."
        lines.append(f"{prefix} {name} – {points} {points_label} ({played})")
    return "\n".join(lines)


STATUS_KEY_MAP = {
    "SCHEDULED": "scheduled",
    "TIMED": "scheduled",
    "IN_PLAY": "live",
    "PAUSED": "paused",
    "FINISHED": "finished",
    "POSTPONED": "postponed",
}


def format_today_matches(lang: str, tz: ZoneInfo) -> str:
    matches = get_today_matches()
    if not matches:
        return t("no_matches", lang)

    lines = [t("today_matches", lang)]
    for m in matches:
        home = m["homeTeam"]["name"]
        away = m["awayTeam"]["name"]
        status_key = STATUS_KEY_MAP.get(m["status"])
        status = t(status_key, lang) if status_key else m["status"]

        score = m.get("score", {}).get("fullTime", {})
        gh, ga = score.get("home"), score.get("away")
        score_str = f" {gh}:{ga}" if gh is not None else ""

        utc_dt = datetime.fromisoformat(m["utcDate"].replace("Z", "+00:00"))
        local_dt = utc_dt.astimezone(tz)
        time_str = local_dt.strftime("%H:%M")

        lines.append(f"{status} {time_str} – {home} vs {away}{score_str}")

    return "\n".join(lines)


def get_match_info(match: Dict[str, Any]) -> Tuple[str, str, Optional[str]]:
    venue = match.get("venue") or "?"
    group = match.get("group")
    stage = match.get("stage", "?")
    stage_display = group if group else stage

    referees = match.get("referees", [])
    referee_name = referees[0]["name"] if referees else None

    return venue, stage_display, referee_name
