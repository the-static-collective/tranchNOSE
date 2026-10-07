#!/usr/bin/env python3
"""GHoT adapter for TranchNOSE FIELD-LAB-001."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.field_lab.field_lab import run_field_lab  # noqa: E402


def main() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("JSON input required")
    request = json.loads(raw)
    receipt = run_field_lab(request)
    receipt_text = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    return {
        "kind": "tranchnose.ghot-field-lab-result",
        "version": "0",
        "capability": "analysis.tranchnose.field-lab",
        "status": "ok",
        "artifact": {
            "receipt_text": receipt_text,
            "receipt_sha256": hashlib.sha256(
                receipt_text.encode("utf-8")
            ).hexdigest(),
        },
        "receipt": receipt,
    }


if __name__ == "__main__":
    try:
        sys.stdout.write(json.dumps(main(), sort_keys=True))
    except Exception as exc:
        sys.stderr.write(
            json.dumps({"error": f"{type(exc).__name__}: {exc}"}) + "\n"
        )
        raise SystemExit(1)
