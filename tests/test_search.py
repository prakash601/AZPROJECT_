"""Tests for search.py – mean_pooling, encode_query, search, autocomplete."""
import numpy as np
import pytest
from unittest import mock


def test_mean_pooling_basic():
    import search

    # token_embeddings shape (batch=1, seq=2, hidden=2)
    model_output = [np.array([[[1.0, 2.0], [3.0, 4.0]]])]
    attention_mask = np.array([[1, 0]])  # only first token counts
    result = search.mean_pooling(model_output, attention_mask)
    # mean of only first token => [[1,2]]
    np.testing.assert_allclose(result, np.array([[1.0, 2.0]]))


def test_mean_pooling_all_masked():
    import search
    model_output = [np.array([[[1.0, 2.0], [3.0, 4.0]]])]
    attention_mask = np.array([[0, 0]])
    result = search.mean_pooling(model_output, attention_mask)
    # sum_mask clipped to 1e-9, so result should be finite (near 0)
    assert result.shape == (1, 2)
    assert np.all(np.isfinite(result))


def test_encode_query_returns_normalized_list(mock_get_cursor):
    import search

    # Mock tokenizer (tokenizers lib interface) and session
    fake_tokenizer = mock.MagicMock()
    fake_enc = mock.MagicMock()
    fake_enc.ids = [1, 2, 3]
    fake_enc.attention_mask = [1, 1, 1]
    fake_enc.type_ids = [0, 0, 0]
    fake_tokenizer.encode.return_value = fake_enc

    fake_session = mock.MagicMock()
    fake_input = mock.MagicMock()
    fake_input.name = "input_ids"
    fake_session.get_inputs.return_value = [fake_input]
    # session.run returns [token_embeddings]; shape (1,3,384)
    token_emb = np.ones((1, 3, 384))
    fake_session.run.return_value = [token_emb]

    with mock.patch("search.get_onnx_model", return_value=(fake_tokenizer, fake_session)):
        vec = search.encode_query("hello world")

    assert isinstance(vec, list)
    assert len(vec) == 384
    # L2 norm should be ~1
    norm = np.linalg.norm(np.array(vec))
    assert abs(norm - 1.0) < 1e-5
    fake_tokenizer.encode.assert_called_once_with("hello world")
    # session fed only the inputs it expects
    run_inputs = fake_session.run.call_args[0][1]
    assert set(run_inputs.keys()) == {"input_ids"}


def test_get_onnx_model_lazy_loads_once():
    import search

    search._tokenizer = None
    search._session = None

    fake_tokenizer = mock.MagicMock()
    fake_session = mock.MagicMock()

    with mock.patch("search.Tokenizer.from_file", return_value=fake_tokenizer) as mock_tok, \
         mock.patch("search._ensure_local_files", return_value="models/onnx-minilm-l6-v2/model.onnx"), \
         mock.patch("onnxruntime.InferenceSession", return_value=fake_session) as mock_sess:
        t1, m1 = search.get_onnx_model()
        t2, m2 = search.get_onnx_model()

        assert t1 is fake_tokenizer
        assert m1 is fake_session
        assert t2 is fake_tokenizer
        # Should only load once
        mock_tok.assert_called_once()
        mock_sess.assert_called_once()


def test_search_calls_cursor_with_correct_params(mock_get_cursor):
    import search

    mock_cur, _ = mock_get_cursor
    # Mock encode_query to avoid ONNX
    with mock.patch("search.encode_query", return_value=[0.1] * 384):
        # Mock fetchall to return one row
        mock_cur.fetchall.return_value = [
            (1, "leetcode", "Two Sum", "https://example.com", "desc", "Easy", ["array"], 0.06)
        ]
        results = search.search("two sum", limit=5, offset=10)

    assert len(results) == 1
    r = results[0]
    assert r["id"] == 1
    assert r["platform"] == "leetcode"
    assert r["tags"] == ["array"]
    assert isinstance(r["score"], float)

    # Verify execute called with 10 params
    assert mock_cur.execute.called
    args, kwargs = mock_cur.execute.call_args
    sql, params = args
    assert "WITH semantic" in sql
    assert len(params) == 10
    assert params[8] == 5  # limit
    assert params[9] == 10  # offset
    # embedding passed twice for semantic
    assert params[0] == [0.1] * 384
    assert params[1] == [0.1] * 384


def test_search_handles_tags_none(mock_get_cursor):
    import search

    mock_cur, _ = mock_get_cursor
    mock_cur.fetchall.return_value = [
        (2, "codeforces", "A + B", "https://cf.com/1", "desc", None, None, 0.03)
    ]
    with mock.patch("search.encode_query", return_value=[0.0] * 384):
        results = search.search("a+b")

    assert results[0]["tags"] == []
    assert results[0]["difficulty"] is None


def test_search_empty_returns_empty(mock_get_cursor):
    import search

    mock_cur, _ = mock_get_cursor
    mock_cur.fetchall.return_value = []
    with mock.patch("search.encode_query", return_value=[0.0] * 384):
        results = search.search("nonexistent xyz")
    assert results == []


def test_autocomplete_calls_cursor_correctly(mock_get_cursor):
    import search

    mock_cur, _ = mock_get_cursor
    mock_cur.fetchall.return_value = [(1, "Two Sum", "https://example.com", "leetcode")]
    results = search.autocomplete("two", limit=7)

    assert results == [{"id": 1, "title": "Two Sum", "url": "https://example.com", "platform": "leetcode"}]
    assert mock_cur.execute.called
    sql, params = mock_cur.execute.call_args[0]
    assert "FROM problems" in sql
    # params: (prefix, like_pattern, like_pattern, prefix, limit)
    assert params == ("two", "two%", "two%", "two", 7)


def test_autocomplete_empty(mock_get_cursor):
    import search

    mock_cur, _ = mock_get_cursor
    mock_cur.fetchall.return_value = []
    results = search.autocomplete("zzz")
    assert results == []
