from pathlib import Path

from allen_neuro_mcp.cache import FileCache


def test_file_cache_writes_json(tmp_path: Path) -> None:
    cache = FileCache(tmp_path)

    path = cache.write_json(
        tmp_path / "example.json",
        {"answer": 42},
    )

    assert path.exists()
    assert '"answer": 42' in path.read_text(encoding="utf-8")


def test_file_cache_creates_bundle_directory(tmp_path: Path) -> None:
    cache = FileCache(tmp_path)

    path = cache.bundle_dir(123)

    assert path.exists()
    assert path.name == "123"
    assert path.parent.name == "bundles"