from unittest.mock import patch

from click.testing import CliRunner

from qnpmusic import config, db
from qnpmusic.main import cli


def test_help_shows_commands(isolated_env):
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ["setup", "create", "add", "import-staging", "playlists", "show", "export", "play"]:
        assert cmd in result.output


def test_create_command(isolated_env):
    runner = CliRunner()
    result = runner.invoke(cli, ["create", "study"])
    assert result.exit_code == 0
    cfg = config.load_config()
    conn = db.connect(cfg)
    row = db.get_playlist_by_name(conn, "study")
    assert row is not None
    conn.close()


def test_add_writes_staging_newest_first(isolated_env):
    runner = CliRunner()
    cfg = config.load_config()
    # set a music dir so staging lives under tmp
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    cfg = config.load_config()
    runner.invoke(cli, ["add", "https://url1", "--playlist", "study"])
    runner.invoke(cli, ["add", "https://url2", "--playlist", "chill"])
    from qnpmusic import staging
    entries = staging.read_entries(config.staging_path(cfg))
    assert entries[0] == ("https://url2", "chill")
    assert entries[1] == ("https://url1", "study")


def test_add_default_playlist(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    cfg = config.load_config()
    runner.invoke(cli, ["add", "https://url1"])
    from qnpmusic import staging
    entries = staging.read_entries(config.staging_path(cfg))
    assert entries == [("https://url1", "default")]


def test_import_staging_validates_and_imports(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    from qnpmusic import staging
    staging.prepend_entry(config.staging_path(cfg), "https://good", "study")
    staging.prepend_entry(config.staging_path(cfg), "https://bad", "study")
    with patch("qnpmusic.player.validate_url", side_effect=lambda u, **kw: u == "https://good"):
        result = runner.invoke(cli, ["import-staging"])
    assert result.exit_code == 0
    conn = db.connect(cfg)
    rows = db.playlist_urls(conn, "study")
    urls = [r["url"] for r in rows]
    assert "https://good" in urls
    assert "https://bad" not in urls
    conn.close()


def test_import_staging_flushes_imported_leaves_failed(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    from qnpmusic import staging
    staging.prepend_entry(config.staging_path(cfg), "https://good", "study")
    staging.prepend_entry(config.staging_path(cfg), "https://bad", "study")
    with patch("qnpmusic.player.validate_url", side_effect=lambda u, **kw: u == "https://good"):
        runner.invoke(cli, ["import-staging"])
    remaining = staging.read_entries(config.staging_path(cfg))
    assert ("https://bad", "study") in remaining
    assert ("https://good", "study") not in remaining


def test_import_staging_skips_duplicates(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    from qnpmusic import staging
    staging.prepend_entry(config.staging_path(cfg), "https://dup", "study")
    with patch("qnpmusic.player.validate_url", return_value=True):
        runner.invoke(cli, ["import-staging"])
    staging.prepend_entry(config.staging_path(cfg), "https://dup", "study")
    with patch("qnpmusic.player.validate_url", return_value=True):
        result = runner.invoke(cli, ["import-staging"])
    assert "SKIP" in result.output
    conn = db.connect(cfg)
    rows = db.playlist_urls(conn, "study")
    assert len(rows) == 1


def test_import_staging_empty(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    result = runner.invoke(cli, ["import-staging"])
    assert result.exit_code == 0
    assert "No staged entries" in result.output


def test_playlists_command(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    runner.invoke(cli, ["create", "study"])
    runner.invoke(cli, ["create", "chill"])
    result = runner.invoke(cli, ["playlists"])
    assert result.exit_code == 0
    assert "study" in result.output
    assert "chill" in result.output


def test_playlists_empty(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    result = runner.invoke(cli, ["playlists"])
    assert "No playlists" in result.output


def test_show_command(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study", title="Song A")
    conn.commit()
    conn.close()
    result = runner.invoke(cli, ["show", "study"])
    assert result.exit_code == 0
    assert "https://x/a" in result.output
    assert "Song A" in result.output


def test_show_empty(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    result = runner.invoke(cli, ["show", "nope"])
    assert "empty or does not exist" in result.output


def test_export_command(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study")
    db.add_song_to_playlist(conn, "https://x/b", "study")
    conn.commit()
    conn.close()
    result = runner.invoke(cli, ["export", "study"])
    assert result.exit_code == 0
    out = config.export_path("study", cfg)
    assert out.exists()
    content = out.read_text()
    assert "https://x/a" in content
    assert "https://x/b" in content


def test_export_with_output_path(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study")
    conn.commit()
    conn.close()
    out = isolated_env / "custom.txt"
    result = runner.invoke(cli, ["export", "study", "--output", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_play_command_invokes_mpv(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    runner.invoke(cli, ["setup", "--music-dir", str(music)])
    cfg = config.load_config()
    conn = db.connect(cfg)
    db.add_song_to_playlist(conn, "https://x/a", "study")
    conn.commit()
    conn.close()
    with patch("qnpmusic.player.play_playlist", return_value=0) as mock_play:
        result = runner.invoke(cli, ["play", "study"])
    assert result.exit_code == 0
    mock_play.assert_called_once()
    args = mock_play.call_args[0][0]
    assert "study" in args or "https://x/a" in args


def test_play_empty_playlist(isolated_env):
    runner = CliRunner()
    runner.invoke(cli, ["setup", "--music-dir", str(isolated_env / "music" / "qnpmusic")])
    result = runner.invoke(cli, ["play", "nope"])
    assert "empty or does not exist" in result.output
