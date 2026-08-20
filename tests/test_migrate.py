"""Tests for migrate.py – read_index_files + batch mogrify insert."""
import pytest
from pathlib import Path
from unittest import mock
from contextlib import contextmanager


def _create_index_files(tmp_path, n=3):
    qdata_dir = tmp_path / "Qdata"
    tfidf_dir = tmp_path / "TFIDF"
    qdata_dir.mkdir(parents=True)
    tfidf_dir.mkdir(parents=True)
    urls = [f"https://example.com/{i}" for i in range(n)]
    titles = [f"Title {i}" for i in range(n)]
    platforms = ["leetcode"] * n
    descriptions = [f"Desc {i}" for i in range(n)]
    (qdata_dir / "Qindex.txt").write_text("\n".join(urls))
    (qdata_dir / "index.txt").write_text("\n".join(titles))
    (tfidf_dir / "platform_name.txt").write_text("\n".join(platforms))
    (tfidf_dir / "qdata.txt").write_text("\n".join(descriptions))
    return qdata_dir, tfidf_dir, urls, titles, platforms, descriptions


def test_read_index_files_success(tmp_path):
    import migrate
    qdata_dir, tfidf_dir, urls, titles, platforms, descriptions = _create_index_files(tmp_path, n=5)
    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir):
        u, t, p, d = migrate.read_index_files()
        assert u == urls
        assert t == titles
        assert p == platforms
        assert d == descriptions


def test_read_index_files_length_mismatch(tmp_path):
    import migrate
    qdata_dir = tmp_path / "Qdata"
    tfidf_dir = tmp_path / "TFIDF"
    qdata_dir.mkdir(parents=True)
    tfidf_dir.mkdir(parents=True)
    (qdata_dir / "Qindex.txt").write_text("a\nb")
    (qdata_dir / "index.txt").write_text("t1")
    (tfidf_dir / "platform_name.txt").write_text("p1\np2")
    (tfidf_dir / "qdata.txt").write_text("d1\nd2")

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir):
        with pytest.raises(AssertionError, match="length mismatch"):
            migrate.read_index_files()


def test_migrate_batch_mogrify_insert(tmp_path):
    import migrate

    qdata_dir, tfidf_dir, urls, titles, platforms, descriptions = _create_index_files(tmp_path, n=3)

    # Mock cursor with mogrify returning bytes
    mock_cur = mock.MagicMock()
    def mogrify_side_effect(query, params):
        # Simulate psycopg2 mogrify: returns b"('leetcode', 'Title 0', ...)"
        return b"('%s', '%s', '%s', '%s')" % tuple(p.encode() if isinstance(p, str) else b"x" for p in params)
    mock_cur.mogrify.side_effect = mogrify_side_effect
    mock_cur.execute.return_value = None

    @contextmanager
    def fake_get_cursor():
        yield mock_cur

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch.object(migrate, "BATCH_SIZE", 2):
        # tqdm is used; patch to avoid output
        with mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
            migrate.migrate()

    # Batch size 2 with 3 rows => 2 batches, 2 execute calls
    assert mock_cur.execute.call_count == 2
    # Verify mogrify called per row (3 times)
    assert mock_cur.mogrify.call_count == 3
    # Verify execute was NOT called via executemany (legacy path)
    assert not mock_cur.executemany.called
    # Check SQL contains ON CONFLICT DO NOTHING and VALUES
    for call in mock_cur.execute.call_args_list:
        sql = call[0][0]
        assert "INSERT INTO problems" in sql
        assert "ON CONFLICT (url) DO NOTHING" in sql
        assert "VALUES" in sql


def test_migrate_skips_empty_url_or_title(tmp_path):
    import migrate

    qdata_dir = tmp_path / "Qdata"
    tfidf_dir = tmp_path / "TFIDF"
    qdata_dir.mkdir(parents=True)
    tfidf_dir.mkdir(parents=True)
    # 3 rows aligned: row1 empty url, row2 empty title, row0 valid
    # Keep 3 lines each file – empty string still counts as a line ("" after rstrip)
    (qdata_dir / "Qindex.txt").write_text("https://example.com/1\n\nhttps://example.com/3")
    (qdata_dir / "index.txt").write_text("Title 1\n\nTitle 3")
    (tfidf_dir / "platform_name.txt").write_text("leetcode\nleetcode\nleetcode")
    (tfidf_dir / "qdata.txt").write_text("Desc 1\nDesc 2\nDesc 3")

    mock_cur = mock.MagicMock()
    mock_cur.mogrify.return_value = b"('p','t','u','d')"
    @contextmanager
    def fake_get_cursor():
        yield mock_cur

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch.object(migrate, "BATCH_SIZE", 10), \
         mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
        migrate.migrate()

    # row0 valid, row1 empty url+title -> skip, row2 valid => 2 inserted
    assert mock_cur.mogrify.call_count == 2


def test_migrate_fallback_description_from_file(tmp_path):
    import migrate

    qdata_dir = tmp_path / "Qdata"
    tfidf_dir = tmp_path / "TFIDF"
    qdata_dir.mkdir(parents=True)
    tfidf_dir.mkdir(parents=True)
    (qdata_dir / "Qindex.txt").write_text("https://example.com/1")
    (qdata_dir / "index.txt").write_text("Title 1")
    (tfidf_dir / "platform_name.txt").write_text("leetcode")
    (tfidf_dir / "qdata.txt").write_text(" ")  # whitespace -> stripped empty triggers fallback

    # Create fallback file Qdata/1/1.txt
    fallback_dir = qdata_dir / "1"
    fallback_dir.mkdir()
    (fallback_dir / "1.txt").write_text("Fallback description")

    mock_cur = mock.MagicMock()
    mock_cur.mogrify.return_value = b"('leetcode','Title 1','https://example.com/1','Fallback description')"
    @contextmanager
    def fake_get_cursor():
        yield mock_cur

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch.object(migrate, "BATCH_SIZE", 10), \
         mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
        migrate.migrate()

    assert mock_cur.mogrify.call_count == 1
    # Verify the description passed to mogrify is fallback
    _, params = mock_cur.mogrify.call_args[0][1], mock_cur.mogrify.call_args[0]
    # mogrify called with (platform, title, url, description)
    assert mock_cur.mogrify.call_args[0][1][3] == "Fallback description"


def test_migrate_skips_when_no_description_even_after_fallback(tmp_path):
    import migrate

    qdata_dir = tmp_path / "Qdata"
    tfidf_dir = tmp_path / "TFIDF"
    qdata_dir.mkdir(parents=True)
    tfidf_dir.mkdir(parents=True)
    (qdata_dir / "Qindex.txt").write_text("https://example.com/1")
    (qdata_dir / "index.txt").write_text("Title 1")
    (tfidf_dir / "platform_name.txt").write_text("leetcode")
    (tfidf_dir / "qdata.txt").write_text(" ")  # whitespace -> skipped even after fallback

    mock_cur = mock.MagicMock()
    mock_cur.mogrify.return_value = b"('x')"
    @contextmanager
    def fake_get_cursor():
        yield mock_cur

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch.object(migrate, "BATCH_SIZE", 10), \
         mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
        migrate.migrate()

    assert mock_cur.mogrify.call_count == 0
    assert mock_cur.execute.call_count == 0


def test_migrate_empty_batch_no_execute(tmp_path):
    import migrate
    # Empty files
    qdata_dir, tfidf_dir, *_ = _create_index_files(tmp_path, n=0)
    mock_cur = mock.MagicMock()
    @contextmanager
    def fake_get_cursor():
        yield mock_cur
    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
        migrate.migrate()
    assert mock_cur.execute.call_count == 0


def test_migrate_mogrify_joins_multiple_rows(tmp_path):
    """Ensure VALUES clause contains comma-separated mogrified tuples."""
    import migrate

    qdata_dir, tfidf_dir, *_ = _create_index_files(tmp_path, n=2)
    mock_cur = mock.MagicMock()
    # Return distinct bytes per row to verify join
    mock_cur.mogrify.side_effect = [b"('a','b','c','d')", b"('e','f','g','h')"]

    @contextmanager
    def fake_get_cursor():
        yield mock_cur

    with mock.patch.object(migrate, "QDATA_DIR", qdata_dir), \
         mock.patch.object(migrate, "TFIDF_DIR", tfidf_dir), \
         mock.patch("migrate.get_cursor", fake_get_cursor), \
         mock.patch.object(migrate, "BATCH_SIZE", 10), \
         mock.patch("migrate.tqdm", side_effect=lambda iterable, **kw: iterable):
        migrate.migrate()

    sql = mock_cur.execute.call_args[0][0]
    # Should contain both tuples joined by comma
    assert "('a','b','c','d'),('e','f','g','h')" in sql
