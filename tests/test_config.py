import json
import pathlib

from click.testing import CliRunner

from qnpmusic import config
from qnpmusic.main import cli


def test_config_dir_uses_xdg(isolated_env):
    assert config.config_dir() == isolated_env / "config" / "qnpmusic"


def test_config_dir_defaults_to_home(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert config.config_dir() == tmp_path / ".config" / "qnpmusic"


def test_setup_writes_config(isolated_env):
    runner = CliRunner()
    music = isolated_env / "music" / "qnpmusic"
    result = runner.invoke(cli, ["setup", "--music-dir", str(music)])
    assert result.exit_code == 0
    cfg = config.load_config()
    assert cfg["music_dir"] == str(music)
    assert cfg["default_playlist"] == "default"
    assert config.config_path().exists()


def test_music_dir_default(isolated_env):
    cfg = {}
    assert config.music_dir(cfg) == pathlib.Path.home() / "Music" / "qnpmusic"


def test_music_dir_from_config(isolated_env):
    cfg = {"music_dir": "/some/path"}
    assert config.music_dir(cfg) == pathlib.Path("/some/path")


def test_slugify():
    assert config.slugify("Late Night Jazz") == "late-night-jazz"
    assert config.slugify("study") == "study"
    assert config.slugify("  Foo Bar!! ") == "foo-bar"
