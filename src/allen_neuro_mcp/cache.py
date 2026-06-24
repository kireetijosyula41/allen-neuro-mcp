import json
from pathlib import Path
from typing import Any

import hashlib


class FileCache:
    """
    Small deterministic file cache for generated Allen Neuro MCP artifacts.

    v0 only writes JSON metadata/ephys bundles.
    Later versions can add SWC, NWB, checksums, and NEURON project files.
    """

    def __init__(self, root: Path | str = ".cache/allen-neuro-mcp") -> None:
        self.root = Path(root).expanduser()

    def bundle_dir(self, specimen_id: int) -> Path:
        path = self.root / "bundles" / str(specimen_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def write_json(path: Path, value: Any) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, indent=2, default=str) + "\n",
            encoding="utf-8",
        )
        return path

    @staticmethod
    def write_text(path: Path, value: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
        return path
    
def sha256_file(path: Path) -> str:
    """
    Compute a SHA256 checksum for a file.

    Used in modeling bundle manifests for reproducibility.
    """

    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()