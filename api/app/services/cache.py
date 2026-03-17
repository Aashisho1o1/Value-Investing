import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any


class FileCache:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str, suffix: str) -> Path:
        slug = re.sub(r"[^a-zA-Z0-9_.-]+", "_", key).strip("_")[:80] or "cache"
        digest = hashlib.md5(key.encode("utf-8")).hexdigest()
        return self.root / f"{slug}_{digest}.{suffix}"

    def load_json(self, key: str, ttl_seconds: int | None = None) -> Any | None:
        path = self._path(key, "json")
        if not path.exists():
            return None

        payload = json.loads(path.read_text())
        if ttl_seconds is not None and time.time() - payload["stored_at"] > ttl_seconds:
            return None
        return payload["value"]

    def save_json(self, key: str, value: Any) -> None:
        path = self._path(key, "json")
        payload = {"stored_at": time.time(), "value": value}
        path.write_text(json.dumps(payload, indent=2))

    def load_text(self, key: str, ttl_seconds: int | None = None) -> str | None:
        path = self._path(key, "txt")
        if not path.exists():
            return None

        payload = json.loads(path.read_text())
        if ttl_seconds is not None and time.time() - payload["stored_at"] > ttl_seconds:
            return None
        return payload["value"]

    def save_text(self, key: str, value: str) -> None:
        path = self._path(key, "txt")
        payload = {"stored_at": time.time(), "value": value}
        path.write_text(json.dumps(payload))

