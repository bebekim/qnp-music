import os
import json
import pathlib

APP_NAME = "qnpmusic"
DEFAULT_PLAYLIST = "default"


def config_dir() -> pathlib.Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return pathlib.Path(xdg) / APP_NAME
    return pathlib.Path.home() / ".config" / APP_NAME


def config_path() -> pathlib.Path:
    return config_dir() / "config.json"


def load_config() -> dict:
    p = config_path()
    if not p.exists():
        return {}
    with p.open() as f:
        return json.load(f)


def save_config(cfg: dict) -> None:
    p = config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w") as f:
        json.dump(cfg, f, indent=2)


def music_dir(cfg: dict | None = None) -> pathlib.Path:
    cfg = cfg if cfg is not None else load_config()
    if cfg.get("music_dir"):
        return pathlib.Path(cfg["music_dir"])
    return pathlib.Path.home() / "Music" / APP_NAME


def db_path(cfg: dict | None = None) -> pathlib.Path:
    return music_dir(cfg) / "qnpmusic.sqlite"


def staging_path(cfg: dict | None = None) -> pathlib.Path:
    return music_dir(cfg) / "staging.tsv"


def playlists_dir(cfg: dict | None = None) -> pathlib.Path:
    return music_dir(cfg) / "playlists"


def export_path(name: str, cfg: dict | None = None) -> pathlib.Path:
    slug = slugify(name)
    return playlists_dir(cfg) / f"{slug}.txt"


def slugify(name: str) -> str:
    import re

    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def default_playlist_name(cfg: dict | None = None) -> str:
    cfg = cfg if cfg is not None else load_config()
    return cfg.get("default_playlist", DEFAULT_PLAYLIST)
