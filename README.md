# qnpmusic

A local CLI for managing music URLs and playing them with `mpv`.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- [mpv](https://mpv.io/) — install with `brew install mpv`

## Install

```bash
uv tool install ~/repositories/individual/qnp-music
```

This puts the `qnpmusic` command on your PATH.

## Setup

```bash
qnpmusic setup --music-dir ~/Music/qnpmusic
```

Creates config at `~/.config/qnpmusic/config.json` and uses `~/Music/qnpmusic` for data (SQLite DB, staging file, exported playlists).

## Usage

```bash
# Create a playlist
qnpmusic create "Late Night Jazz"

# Add a URL to staging (quotes needed for & in URLs)
qnpmusic add 'https://www.youtube.com/watch?v=...' --playlist "Late Night Jazz"

# Omit --playlist to stage into the default playlist
qnpmusic add 'https://www.youtube.com/watch?v=...'

# Validate staged URLs with mpv and import working ones into SQLite
qnpmusic import-staging

# List all playlists
qnpmusic playlists

# Show songs in a playlist
qnpmusic show "Late Night Jazz"

# Export a playlist to an mpv playlist file
qnpmusic export study

# Play a playlist (foreground, blocks until you quit mpv)
qnpmusic play study
```

## How it works

1. **`add`** writes URLs to a staging file (`staging.tsv`), newest first. Nothing goes into the database yet.
2. **`import-staging`** validates each staged URL by running `mpv --length=10` on it. Working URLs are imported into SQLite, broken ones stay in staging.
3. **`play`** exports the playlist to a temporary file and launches `mpv --no-video --loop-playlist=inf` in the foreground.

## Files

| Path | Purpose |
|---|---|
| `~/.config/qnpmusic/config.json` | Config (music dir, default playlist) |
| `~/Music/qnpmusic/qnpmusic.sqlite` | SQLite database (source of truth) |
| `~/Music/qnpmusic/staging.tsv` | Temporary staging file (URL + playlist, tab-separated) |
| `~/Music/qnpmusic/playlists/` | Exported mpv playlist files |

## Development

```bash
cd ~/repositories/individual/qnp-music
uv sync
uv run pytest
```
