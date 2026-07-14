from imj import config, db


def test_schema_created(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
    }
    assert {"songs", "playlists", "playlist_songs", "play_history"} <= tables
    conn.close()


def test_create_playlist_idempotent(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    id1 = db.get_or_create_playlist(conn, "study")
    id2 = db.get_or_create_playlist(conn, "study")
    assert id1 == id2
    conn.close()


def test_add_song_to_playlist(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    created = db.add_song_to_playlist(conn, "https://x/a", "study")
    assert created is True
    rows = db.playlist_urls(conn, "study")
    assert len(rows) == 1
    assert rows[0]["url"] == "https://x/a"
    conn.close()


def test_duplicate_url_same_playlist(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study")
    created = db.add_song_to_playlist(conn, "https://x/a", "study")
    assert created is False
    rows = db.playlist_urls(conn, "study")
    assert len(rows) == 1
    conn.close()


def test_same_url_different_playlists(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study")
    db.add_song_to_playlist(conn, "https://x/a", "chill")
    assert len(db.playlist_urls(conn, "study")) == 1
    assert len(db.playlist_urls(conn, "chill")) == 1
    conn.close()


def test_position_preserves_order(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/1", "study")
    db.add_song_to_playlist(conn, "https://x/2", "study")
    db.add_song_to_playlist(conn, "https://x/3", "study")
    urls = [r["url"] for r in db.playlist_urls(conn, "study")]
    assert urls == ["https://x/1", "https://x/2", "https://x/3"]
    conn.close()


def test_list_playlists(isolated_env):
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.get_or_create_playlist(conn, "chill")
    db.get_or_create_playlist(conn, "study")
    names = [r["name"] for r in db.list_playlists(conn)]
    assert names == ["chill", "study"]
    conn.close()
