#!/usr/bin/env python3
"""Rerun the v0.3 tamper suite from an already-built content kit.

This script is intentionally thin: the built package already includes generated tamper cases
and reports.  For reproducible tamper generation, rerun /mnt/data/build_paper2_content_v0_3.py
or port the build-time tamper functions into a project test suite.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--report", default="outputs/tamper_suite_report.json")
    args = p.parse_args()
    report_path = Path(args.report)
    if not report_path.exists():
        raise SystemExit(f"missing report: {report_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    print(json.dumps(report.get("counts", {}), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
