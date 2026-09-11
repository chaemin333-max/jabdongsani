#!/usr/bin/env python3
from pathlib import Path
import base64
import gzip
import hashlib

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "Maple/data/raw"
OUT = ROOT / "Maple/data/meso_total_production_raw_canonical.json"
PARTS = [RAW / f"meso_total_production_raw_canonical.part{i:02d}.b64" for i in range(4)]
EXPECTED_SHA256 = "63e41f7c7d5c384971524a56df0dcc01a25fd888f808e9174b3195feb9dd6b41"

payload = "".join(p.read_text(encoding="utf-8").strip() for p in PARTS)
raw = gzip.decompress(base64.b64decode(payload))
sha = hashlib.sha256(raw).hexdigest()
if sha != EXPECTED_SHA256:
    raise RuntimeError(f"SHA256 mismatch: {sha} != {EXPECTED_SHA256}")
OUT.write_bytes(raw)
print(f"restored {OUT}")
print(f"sha256 {sha}")
