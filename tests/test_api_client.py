from bot.api_client import format_table


def test_format_table_none_returns_none():
    assert format_table(None, "en") is None


def test_format_table_basic():
    group = {
        "group": "Group A",
        "table": [
            {"team": {"name": "Germany"}, "points": 6, "playedGames": 2},
            {"team": {"name": "France"}, "points": 3, "playedGames": 2},
        ],
    }
    result = format_table(group, "en")
    assert "Table Group A" in result
    assert "Germany – 6 points (2)" in result
    assert "🥇" in result
    assert "🥈" in result
