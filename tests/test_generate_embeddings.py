"""Tests for generate_embeddings.py"""
import pytest
from unittest import mock
from contextlib import contextmanager
import numpy as np


def test_generate_embeddings_no_rows():
    import generate_embeddings

    mock_cur = mock.MagicMock()
    mock_cur.fetchone.return_value = [0]  # total 0
    mock_cur.fetchall.return_value = []

    @contextmanager
    def fake_get_cursor(commit=False):
        yield mock_cur

    with mock.patch("generate_embeddings.get_cursor", fake_get_cursor), \
         mock.patch("generate_embeddings.SentenceTransformer") as mock_st:
        generate_embeddings.generate_embeddings()
        mock_st.assert_called_once()
        # No fetchall loop beyond count
        mock_cur.execute.assert_called_once_with("SELECT COUNT(*) FROM problems WHERE embedding IS NULL")


def test_generate_embeddings_batches_and_commits():
    import generate_embeddings

    mock_cur = mock.MagicMock()
    mock_cur.fetchone.return_value = [2]
    # First fetchall returns 2 rows, second returns empty to break loop
    mock_cur.fetchall.side_effect = [
        [(1, "Title 1", "Desc 1"), (2, "Title 2", "Desc 2")],
        []
    ]
    mock_cur.connection = mock.MagicMock()
    mock_cur.connection.commit = mock.MagicMock()

    fake_embeddings = np.array([[0.1]*384, [0.2]*384])

    mock_model = mock.MagicMock()
    mock_model.encode.return_value = fake_embeddings

    @contextmanager
    def fake_get_cursor(commit=False):
        yield mock_cur

    with mock.patch("generate_embeddings.get_cursor", fake_get_cursor), \
         mock.patch("generate_embeddings.SentenceTransformer", return_value=mock_model) as mock_st, \
         mock.patch("generate_embeddings.tqdm") as mock_tqdm:
        # tqdm context manager mock
        mock_tqdm.return_value.__enter__ = mock.MagicMock(return_value=mock.MagicMock(update=mock.MagicMock()))
        mock_tqdm.return_value.__exit__ = mock.MagicMock(return_value=False)

        generate_embeddings.generate_embeddings()

        # Model called with combined title+desc
        assert mock_model.encode.called
        texts_arg = mock_model.encode.call_args[0][0]
        assert "Title 1" in texts_arg[0]
        assert "Title 2" in texts_arg[1]
        # executemany called to update embeddings
        assert mock_cur.executemany.called
        update_sql, data = mock_cur.executemany.call_args[0]
        assert "UPDATE problems SET embedding" in update_sql
        assert len(data) == 2
        # Commit per batch + final HNSW index commit
        assert mock_cur.connection.commit.call_count >= 2
        # HNSW index creation executed
        hnsw_calls = [c for c in mock_cur.execute.call_args_list if "CREATE INDEX" in str(c)]
        assert len(hnsw_calls) == 1
        assert "vector_cosine_ops" in str(hnsw_calls[0])


def test_generate_embeddings_truncates_description():
    import generate_embeddings

    long_desc = "x" * 5000
    mock_cur = mock.MagicMock()
    mock_cur.fetchone.return_value = [1]
    mock_cur.fetchall.side_effect = [
        [(1, "Title", long_desc)],
        []
    ]
    mock_cur.connection = mock.MagicMock()
    mock_cur.connection.commit = mock.MagicMock()

    fake_emb = np.array([[0.1]*384])
    mock_model = mock.MagicMock()
    mock_model.encode.return_value = fake_emb

    @contextmanager
    def fake_get_cursor(commit=False):
        yield mock_cur

    with mock.patch("generate_embeddings.get_cursor", fake_get_cursor), \
         mock.patch("generate_embeddings.SentenceTransformer", return_value=mock_model), \
         mock.patch("generate_embeddings.tqdm") as mock_tqdm:
        mock_tqdm.return_value.__enter__ = mock.MagicMock(return_value=mock.MagicMock(update=mock.MagicMock()))
        mock_tqdm.return_value.__exit__ = mock.MagicMock(return_value=False)

        generate_embeddings.generate_embeddings()

        texts = mock_model.encode.call_args[0][0]
        # desc truncated to 1000 chars
        assert len(texts[0]) <= len("Title. ") + 1000
        assert texts[0].startswith("Title. ")
