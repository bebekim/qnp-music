import pathlib

from imj import config


def read_entries(path: pathlib.Path) -> list[tuple[str, str]]:
    """Read staging file, return list of (url, playlist) tuples in file order."""
    if not path.exists():
        return []
    entries = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "\t" not in line:
            continue
        url, playlist = line.split("\t", 1)
        entries.append((url.strip(), playlist.strip()))
    return entries


def prepend_entry(path: pathlib.Path, url: str, playlist: str) -> None:
    """Insert a new entry at the top of the staging file."""
    existing = path.read_text() if path.exists() else ""
    line = f"{url}\t{playlist}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(line + existing)


def flush_entries(path: pathlib.Path, to_remove: list[tuple[str, str]]) -> None:
    """Remove successfully imported entries, leave the rest."""
    remove_set = {(u, p) for u, p in to_remove}
    if not path.exists():
        return
    kept = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            kept.append(line)
            continue
        if "\t" not in line:
            kept.append(line)
            continue
        url, playlist = line.split("\t", 1)
        if (url.strip(), playlist.strip()) in remove_set:
            continue
        kept.append(line)
    path.write_text("\n".join(kept) + ("\n" if kept else ""))
