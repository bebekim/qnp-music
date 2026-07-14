import sqlite3
import pathlib

from qnpmusic import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS songs (
  id integer primary key,
  url text not null unique,
  title text
);

CREATE TABLE IF NOT EXISTS playlists (
  id integer primary key,
  name text not null unique,
  slug text not null unique
);

CREATE TABLE IF NOT EXISTS playlist_songs (
  playlist_id integer not null references playlists(id),
  song_id integer not null references songs(id),
  position integer,
  primary key (playlist_id, song_id)
);

CREATE TABLE IF NOT EXISTS play_history (
  id integer primary key,
  song_id integer not null references songs(id),
  played_at text not null
);
"""


def connect(cfg: dict | None = None) -> sqlite3.Connection:
    p = config.db_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(p)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def get_or_create_playlist(conn: sqlite3.Connection, name: str) -> int:
    slug = config.slugify(name)
    row = conn.execute(
        "SELECT id FROM playlists WHERE name = ?", (name,)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute(
        "INSERT INTO playlists (name, slug) VALUES (?, ?)", (name, slug)
    )
    return cur.lastrowid


def get_playlist_by_name(conn: sqlite3.Connection, name: str):
    return conn.execute(
        "SELECT * FROM playlists WHERE name = ?", (name,)
    ).fetchone()


def add_song_to_playlist(conn: sqlite3.Connection, url: str, playlist_name: str, title: str | None = None) -> bool:
    """Insert url into songs (if not duplicate) and link to playlist. Returns True if a new link was created."""
    pid = get_or_create_playlist(conn, playlist_name)
    song = conn.execute("SELECT id FROM songs WHERE url = ?", (url,)).fetchone()
    if song:
        sid = song["id"]
        if title:
            conn.execute("UPDATE songs SET title = ? WHERE id = ?", (title, sid))
    else:
        cur = conn.execute(
            "INSERT INTO songs (url, title) VALUES (?, ?)", (url, title)
        )
        sid = cur.lastrowid
    existing = conn.execute(
        "SELECT 1 FROM playlist_songs WHERE playlist_id = ? AND song_id = ?",
        (pid, sid),
    ).fetchone()
    if existing:
        return False
    pos = conn.execute(
        "SELECT COALESCE(MAX(position), 0) + 1 AS next_pos FROM playlist_songs WHERE playlist_id = ?",
        (pid,),
    ).fetchone()["next_pos"]
    conn.execute(
        "INSERT INTO playlist_songs (playlist_id, song_id, position) VALUES (?, ?, ?)",
        (pid, sid, pos),
    )
    return True


def list_playlists(conn: sqlite3.Connection):
    return conn.execute(
        "SELECT name, slug FROM playlists ORDER BY name"
    ).fetchall()


def playlist_urls(conn: sqlite3.Connection, playlist_name: str):
    return conn.execute(
        """
        SELECT s.url, s.title FROM songs s
        JOIN playlist_songs ps ON ps.song_id = s.id
        JOIN playlists p ON p.id = ps.playlist_id
        WHERE p.name = ?
        ORDER BY ps.position
        """,
        (playlist_name,),
    ).fetchall()
