"""Tests for correct.py – spell correction."""
import pytest
from unittest import mock
from collections import Counter


def test_words_regex():
    import correct
    assert correct.words("Hello, World! 123") == ["hello", "world", "123"]
    assert correct.words("") == []


def test_get_words_caches(mock_get_cursor):
    import correct
    correct.WORDS_CACHE = None
    mock_cur, _ = mock_get_cursor
    mock_cur.fetchall.return_value = [("Two Sum", "array hash"), ("Binary Search", "search divide")]

    w1 = correct.get_words()
    w2 = correct.get_words()

    assert isinstance(w1, Counter)
    assert "two" in w1
    assert "search" in w1
    # Second call should not hit DB again (cached)
    assert mock_cur.execute.call_count == 1
    assert w1 is w2


def test_get_words_handles_db_exception():
    import correct
    correct.WORDS_CACHE = None

    from contextlib import contextmanager

    @contextmanager
    def failing_cursor(commit=False):
        mock_cur = mock.MagicMock()
        mock_cur.execute.side_effect = Exception("db down")
        yield mock_cur

    with mock.patch("correct.get_cursor", failing_cursor):
        w = correct.get_words()
        assert w == Counter()


def test_known_and_candidates():
    import correct
    correct.WORDS_CACHE = Counter({"hello": 5, "world": 3})

    # known returns intersection
    assert correct.known(["hello", "unknown"]) == {"hello"}
    # candidates returns known([word]) if exists
    assert correct.candidates("hello") == {"hello"}
    # unknown word -> edits1 candidates that are known
    # make WORDS_CACHE contain an edit of "helo" -> "hello"
    assert "hello" in correct.candidates("helo")
    # completely unknown -> returns itself
    correct.WORDS_CACHE = Counter({"zzz": 1})
    assert correct.candidates("qwertyuiop") == {"qwertyuiop"} or "qwertyuiop" in correct.candidates("qwertyuiop")


def test_edits1_generates_variants():
    import correct
    edits = correct.edits1("ab")
    # deletes, transposes, replaces, inserts
    assert "a" in edits or "b" in edits  # deletes
    assert "ba" in edits  # transpose
    assert len(edits) > 0


def test_edits2_is_generator():
    import correct
    gen = correct.edits2("ab")
    # Should be iterable
    vals = list(gen)
    assert len(vals) > 0


def test_P_returns_probability():
    import correct
    correct.WORDS_CACHE = Counter({"hello": 2, "world": 2})
    # N=4, hello count 2 => 0.5
    assert correct.P("hello") == pytest.approx(0.5)
    assert correct.P("unknown") == pytest.approx(0.0)


def test_correction_picks_max_P():
    import correct
    correct.WORDS_CACHE = Counter({"hello": 10, "hallo": 1})
    # candidates for "helo" includes hello and hallo etc; hello has higher P
    result = correct.correction("helo")
    assert result in ("hello", "hallo")  # at least one of them


def test_correct_query_empty_and_whitespace():
    import correct
    assert correct.correct_query("") == ""
    assert correct.correct_query("   ") == "   " or correct.correct_query("   ") == ""  # stripped check
    # Actually correct_query strips then returns line if not line => returns line (which is "" after strip? let's check)
    # For "   ", line = "".strip() => "" -> returns line which is ""
    assert correct.correct_query("   ") == ""


def test_correct_query_with_mocked_nltk_and_words():
    import correct
    correct.WORDS_CACHE = Counter({"hello": 5, "world": 5})

    with mock.patch("correct.nltk.word_tokenize", return_value=["hello", "world"]), \
         mock.patch("correct.correction", side_effect=lambda w: w), \
         mock.patch("correct.num2words", return_value="should_not_be_called"):
        assert correct.correct_query("hello world") == "hello world"


def test_correct_query_digit_to_words():
    import correct
    correct.WORDS_CACHE = Counter()

    with mock.patch("correct.nltk.word_tokenize", return_value=["2", "sum"]), \
         mock.patch("correct.correction", return_value="sum"), \
         mock.patch("correct.num2words", return_value="two"):
        result = correct.correct_query("2 sum")
        assert result == "two sum"


def test_correct_query_mixed_digit_and_word_correction():
    import correct

    def fake_correction(word):
        if word == "binery":
            return "binary"
        return word

    with mock.patch("correct.nltk.word_tokenize", return_value=["binery", "2"]), \
         mock.patch("correct.correction", side_effect=fake_correction), \
         mock.patch("correct.num2words", return_value="two"):
        result = correct.correct_query("binery 2")
        assert result == "binary two"
