import subprocess
from unittest.mock import patch

from qnpmusic import player


def test_validate_url_success():
    with patch("qnpmusic.player.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0
        )
        assert player.validate_url("https://x") is True


def test_validate_url_failure():
    with patch("qnpmusic.player.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1
        )
        assert player.validate_url("https://x") is False


def test_validate_url_timeout():
    with patch(
        "qnpmusic.player.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="mpv", timeout=20),
    ):
        assert player.validate_url("https://x") is False


def test_mpv_available():
    with patch("qnpmusic.player.shutil.which", return_value="/usr/bin/mpv"):
        assert player.mpv_available() is True
    with patch("qnpmusic.player.shutil.which", return_value=None):
        assert player.mpv_available() is False
