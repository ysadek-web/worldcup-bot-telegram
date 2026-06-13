import time

from bot.logging_config import setup_logging, get_logger
from bot.storage import load_users, save_users, load_state, save_state
from bot.telegram_client import get_updates
from bot.handlers import process_updates
from bot.match_tracker import process_match
from bot.api_client import get_today_matches
from bot.config import POLL_INTERVAL

setup_logging()
logger = get_logger(__name__)


def main_loop() -> None:
    users = load_users()
    state = load_state()
    last_update_id = state.get("last_update_id")
    last_match_check = 0.0

    logger.info("Bot gestartet. Aktuelle Nutzer: %d", len(users))

    while True:
        try:
            updates = get_updates(last_update_id)
            if updates:
                new_last_id = process_updates(updates, users)
                if new_last_id is not None:
                    last_update_id = new_last_id
                    state["last_update_id"] = last_update_id
                    save_users(users)
                    save_state(state)

            now = time.time()
            if now - last_match_check >= POLL_INTERVAL:
                matches = get_today_matches()
                state_changed = False
                for match in matches:
                    if process_match(match, users, state):
                        state_changed = True
                if state_changed:
                    save_state(state)
                last_match_check = now

        except Exception:
            logger.exception("Unerwarteter Fehler in der Haupt-Loop")

        time.sleep(3)


if __name__ == "__main__":
    main_loop()
