"""Content hashes for tracing exact input and output file versions."""

import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Return SHA-256 of the bytes of a file, without changing it."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
