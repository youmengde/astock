import json

from astock import watchlist


def test_add_and_list(tmp_path, monkeypatch):
    wl_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(watchlist, "WATCHLIST_FILE", wl_file)
    monkeypatch.setattr(watchlist, "WATCHLIST_DIR", tmp_path)

    assert watchlist.list_codes() == []
    assert watchlist.add("000001") is True
    assert watchlist.add("000001") is False  # duplicate
    assert watchlist.add("600519") is True
    assert watchlist.list_codes() == ["000001", "600519"]


def test_remove(tmp_path, monkeypatch):
    wl_file = tmp_path / "watchlist.json"
    monkeypatch.setattr(watchlist, "WATCHLIST_FILE", wl_file)
    monkeypatch.setattr(watchlist, "WATCHLIST_DIR", tmp_path)

    watchlist.add("000001")
    assert watchlist.remove("000001") is True
    assert watchlist.remove("000001") is False
    assert watchlist.list_codes() == []


def test_corrupted_file_returns_empty(tmp_path, monkeypatch):
    wl_file = tmp_path / "watchlist.json"
    wl_file.write_text("not json{{{", encoding="utf-8")
    monkeypatch.setattr(watchlist, "WATCHLIST_FILE", wl_file)

    assert watchlist.list_codes() == []


def test_deduplicate_on_save(tmp_path, monkeypatch):
    wl_file = tmp_path / "watchlist.json"
    wl_file.write_text(json.dumps(["000001", "000001", "600519"]), encoding="utf-8")
    monkeypatch.setattr(watchlist, "WATCHLIST_FILE", wl_file)
    monkeypatch.setattr(watchlist, "WATCHLIST_DIR", tmp_path)

    # re-save triggers dedup
    watchlist.add("000002")
    assert watchlist.list_codes() == ["000001", "600519", "000002"]
