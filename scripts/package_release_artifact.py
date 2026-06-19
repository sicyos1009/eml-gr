#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, os, zipfile
from pathlib import Path

EXCLUDE_PARTS = {'.git','__pycache__','.pytest_cache'}
EXCLUDE_SUFFIXES = {'.pyc'}

def should_include(p: Path) -> bool:
    if any(part in EXCLUDE_PARTS for part in p.parts):
        return False
    if p.suffix in EXCLUDE_SUFFIXES:
        return False
    if p.name.endswith('.zip'):
        return False
    if p.name == 'CHECKSUMS.sha256':
        return False
    return True

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default='.')
    ap.add_argument('--output', required=True)
    ap.add_argument('--sha-output')
    ns=ap.parse_args()
    root=Path(ns.root).resolve()
    out=Path(ns.output).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    files=[]
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.resolve()!=out and should_include(p.relative_to(root)):
            files.append(p)
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p,p.relative_to(root).as_posix())
    h=sha256_file(out)
    if ns.sha_output:
        Path(ns.sha_output).write_text(h+'\n',encoding='utf-8')
    print(h)
    return 0
if __name__=='__main__':
    raise SystemExit(main())
