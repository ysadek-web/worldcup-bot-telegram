from bot.translations import t, TEXTS


def test_all_keys_have_required_languages():
    required_langs = {"de", "en", "fr", "ar"}
    for key, translations in TEXTS.items():
        missing = required_langs - set(translations.keys())
        assert not missing, f"Key '{key}' fehlt Sprachen: {missing}"


def test_t_returns_correct_language():
    assert t("lang_set", "de") == "✅ Sprache auf Deutsch gesetzt."
    assert t("lang_set", "en") == "✅ Language set to English."


def test_t_fallback_to_english():
    assert t("lang_set", "xx") == TEXTS["lang_set"]["en"]


def test_t_formats_placeholders():
    result = t("goal", "en", home="France", away="Germany", gh=1, ga=0)
    assert result == "⚽ Goal! France 1:0 Germany"
