import pathlib

import click

from qnpmusic import config, db, staging, player


@click.group()
def cli():
    """qnpmusic - local music URL playlist manager with mpv playback."""


@cli.command()
@click.option("--music-dir", "music_dir", default=None, help="Music data directory.")
def setup(music_dir):
    """Write config. Sets the music directory."""
    cfg = config.load_config()
    if music_dir:
        cfg["music_dir"] = str(music_dir)
    if "default_playlist" not in cfg:
        cfg["default_playlist"] = config.DEFAULT_PLAYLIST
    config.save_config(cfg)
    click.echo(f"Config written to {config.config_path()}")
    click.echo(f"Music directory: {config.music_dir(cfg)}")


@cli.command()
@click.argument("name")
def create(name):
    """Create a named playlist."""
    conn = db.connect()
    db.get_or_create_playlist(conn, name)
    conn.commit()
    click.echo(f"Created playlist '{name}'.")
    conn.close()


@cli.command()
@click.argument("url")
@click.option("--playlist", "playlist", default=None, help="Target playlist name.")
def add(url, playlist):
    """Add a URL to the staging file (newest-first). Does not write to SQLite."""
    cfg = config.load_config()
    pname = playlist or config.default_playlist_name(cfg)
    path = config.staging_path(cfg)
    staging.prepend_entry(path, url, pname)
    click.echo(f"Staged '{url}' for playlist '{pname}'.")


@cli.command(name="import-staging")
def import_staging():
    """Validate staged entries with mpv, import working non-duplicates, flush them."""
    if not player.mpv_available():
        raise click.ClickException("mpv needs to be installed or upgraded.")
    cfg = config.load_config()
    path = config.staging_path(cfg)
    entries = staging.read_entries(path)
    if not entries:
        click.echo("No staged entries to import.")
        return
    conn = db.connect(cfg)
    imported = []
    failed = []
    seen = set()
    for url, pname in entries:
        key = (url, pname)
        if key in seen:
            continue
        seen.add(key)
        if not player.validate_url(url):
            failed.append((url, pname))
            click.echo(f"FAIL  {url} (validation)")
            continue
        created = db.add_song_to_playlist(conn, url, pname)
        if created:
            imported.append((url, pname))
            click.echo(f"OK    {url} -> {pname}")
        else:
            click.echo(f"SKIP  {url} -> {pname} (already in playlist)")
    conn.commit()
    staging.flush_entries(path, imported)
    conn.close()
    click.echo(f"Imported {len(imported)}, failed {len(failed)}.")


@cli.command()
def playlists():
    """List all playlists."""
    conn = db.connect()
    rows = db.list_playlists(conn)
    conn.close()
    if not rows:
        click.echo("No playlists.")
        return
    for row in rows:
        click.echo(f"{row['name']}\t{row['slug']}")


@cli.command()
@click.argument("name")
def show(name):
    """Print URLs and titles for a playlist."""
    conn = db.connect()
    rows = db.playlist_urls(conn, name)
    conn.close()
    if not rows:
        click.echo(f"Playlist '{name}' is empty or does not exist.")
        return
    for row in rows:
        title = row["title"] or ""
        click.echo(f"{row['url']}\t{title}")


@cli.command()
@click.option("--output", "output", default=None, help="Output file path.")
@click.argument("name")
def export(name, output):
    """Write an mpv playlist file for NAME."""
    cfg = config.load_config()
    conn = db.connect(cfg)
    rows = db.playlist_urls(conn, name)
    conn.close()
    if not rows:
        click.echo(f"Playlist '{name}' is empty or does not exist.")
        return
    out = pathlib.Path(output) if output else config.export_path(name, cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(row["url"] for row in rows) + "\n")
    click.echo(f"Exported {len(rows)} entries to {out}")


@cli.command()
@click.argument("name")
def play(name):
    """Play a playlist with mpv (no video, infinite loop)."""
    if not player.mpv_available():
        raise click.ClickException("mpv needs to be installed or upgraded.")
    cfg = config.load_config()
    conn = db.connect(cfg)
    rows = db.playlist_urls(conn, name)
    conn.close()
    if not rows:
        click.echo(f"Playlist '{name}' is empty or does not exist.")
        return
    out = config.export_path(name, cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(row["url"] for row in rows) + "\n")
    player.play_playlist(str(out))
