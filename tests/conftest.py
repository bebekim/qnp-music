import pytest


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Isolate XDG config and music dir to temp paths. No real user files touched."""
    cfg_dir = tmp_path / "config"
    music_dir = tmp_path / "music"
    cfg_dir.mkdir()
    music_dir.mkdir()
    monkeypatch.setenv("XDG_CONFIG_HOME", str(cfg_dir))
    monkeypatch.setenv("HOME", str(tmp_path))
    return tmp_path
