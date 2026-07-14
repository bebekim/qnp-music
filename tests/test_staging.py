from imj import config, staging


def test_prepend_entry_newest_first(isolated_env):
    cfg = config.load_config()
    path = config.staging_path(cfg)
    staging.prepend_entry(path, "https://url1", "study")
    staging.prepend_entry(path, "https://url2", "chill")
    entries = staging.read_entries(path)
    assert entries == [("https://url2", "chill"), ("https://url1", "study")]


def test_read_ignores_blank_and_comments(isolated_env):
    cfg = config.load_config()
    path = config.staging_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# a comment\n"
        "\n"
        "https://url1\tstudy\n"
        "https://url2\tchill\n"
    )
    entries = staging.read_entries(path)
    assert len(entries) == 2


def test_flush_removes_only_imported(isolated_env):
    cfg = config.load_config()
    path = config.staging_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "https://good\tstudy\n"
        "https://bad\tstudy\n"
        "https://good2\tchill\n"
    )
    staging.flush_entries(path, [("https://good", "study"), ("https://good2", "chill")])
    remaining = staging.read_entries(path)
    assert remaining == [("https://bad", "study")]


def test_flush_keeps_comments(isolated_env):
    cfg = config.load_config()
    path = config.staging_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# keep me\nhttps://good\tstudy\n")
    staging.flush_entries(path, [("https://good", "study")])
    text = path.read_text()
    assert "# keep me" in text


def test_playlist_names_with_spaces(isolated_env):
    cfg = config.load_config()
    path = config.staging_path(cfg)
    staging.prepend_entry(path, "https://x", "Late Night Jazz")
    entries = staging.read_entries(path)
    assert entries == [("https://x", "Late Night Jazz")]
