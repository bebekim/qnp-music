import shutil
import subprocess

MPV_PLAYBACK_TIMEOUT = None
MPV_VALIDATE_TIMEOUT = 20


def mpv_available() -> bool:
    return shutil.which("mpv") is not None


def validate_url(url: str, timeout: int = MPV_VALIDATE_TIMEOUT) -> bool:
    """Run mpv for ~10s on the URL. Exit 0 within timeout = working."""
    if not mpv_available():
        return False
    try:
        result = subprocess.run(
            ["mpv", "--no-video", "--length=10", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False


def play_playlist(playlist_file: str) -> int:
    """Foreground mpv playlist playback with infinite loop. Returns exit code."""
    if not mpv_available():
        click_error = "mpv needs to be installed or upgraded."
        raise SystemExit(click_error)
    result = subprocess.run(
        ["mpv", "--no-video", "--loop-playlist=inf", f"--playlist={playlist_file}"]
    )
    return result.returncode
