from __future__ import annotations
import hashlib, json, os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "eml-gr-external-ci-result/1.0.0"

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()

def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def result_hash(record: dict) -> str:
    tmp = dict(record)
    tmp.pop('result_hash', None)
    return hashlib.sha256(canonical_json(tmp).encode('utf-8')).hexdigest()[:16]

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + '\n', encoding='utf-8')

def is_hex_sha(s: str, n: int = 64) -> bool:
    return isinstance(s, str) and len(s) == n and all(c in '0123456789abcdef' for c in s)
