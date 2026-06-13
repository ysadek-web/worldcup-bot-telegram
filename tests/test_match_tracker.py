from unittest.mock import patch

from bot.match_tracker import process_match


def base_state():
    return {
        "sent_start": [],
        "sent_halftime": [],
        "sent_finish": [],
        "table_sent": [],
        "last_score": {},
        "last_update_id": None,
    }


def base_match(status="SCHEDULED", gh=None, ga=None):
    return {
        "id": 12345,
        "status": status,
        "homeTeam": {"name": "Germany"},
        "awayTeam": {"name": "France"},
        "score": {"fullTime": {"home": gh, "away": ga}, "halfTime": {"home": None, "away": None}},
        "group": "Group A",
        "venue": "Stadium",
        "stage": "GROUP_STAGE",
        "referees": [],
    }


@patch("bot.match_tracker.send_message_to")
@patch("bot.match_tracker.get_subscribed_users", return_value={})
def test_scheduled_match_no_changes(mock_users, mock_send):
    state = base_state()
    match = base_match(status="SCHEDULED")
    changed = process_match(match, {}, state)
    assert changed is False
    mock_send.assert_not_called()


@patch("bot.match_tracker.broadcast")
@patch("bot.match_tracker.get_subscribed_users", return_value={})
@patch("bot.match_tracker.send_message_to")
def test_match_start_sets_state(mock_send, mock_users, mock_broadcast):
    state = base_state()
    match = base_match(status="IN_PLAY", gh=0, ga=0)
    changed = process_match(match, {}, state)
    assert changed is True
    assert "12345" in state["sent_start"]


@patch("bot.match_tracker.broadcast")
@patch("bot.match_tracker.get_subscribed_users", return_value={})
@patch("bot.match_tracker.send_message_to")
def test_goal_detection(mock_send, mock_users, mock_broadcast):
    state = base_state()
    state["sent_start"] = ["12345"]
    state["last_score"] = {"12345": [0, 0]}

    match = base_match(status="IN_PLAY", gh=1, ga=0)
    changed = process_match(match, {}, state)

    assert changed is True
    assert state["last_score"]["12345"] == [1, 0]
    mock_broadcast.assert_called_with({}, "goal", home="Germany", away="France", gh=1, ga=0)


@patch("bot.match_tracker.broadcast_table")
@patch("bot.match_tracker.get_standings_by_group", return_value=None)
@patch("bot.match_tracker.broadcast")
@patch("bot.match_tracker.get_subscribed_users", return_value={})
@patch("bot.match_tracker.send_message_to")
def test_match_finish_triggers_finish_and_table(
    mock_send, mock_users, mock_broadcast, mock_standings, mock_broadcast_table
):
    state = base_state()
    state["sent_start"] = ["12345"]
    state["last_score"] = {"12345": [1, 0]}

    match = base_match(status="FINISHED", gh=1, ga=0)
    changed = process_match(match, {}, state)

    assert changed is True
    assert "12345" in state["sent_finish"]
    assert "12345" in state["table_sent"]
    mock_broadcast_table.assert_called_once()
