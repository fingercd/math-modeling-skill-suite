"""从 Skyler-Luo/CUMCM2025-B 抓取四个附件,本地落盘 ./data/附件N.csv

URL 中的中文路径使用 percent-encoding 规避 Windows 默认编码在 urlopen 上的问题。
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen, Request

BASE = "https://raw.githubusercontent.com/Skyler-Luo/CUMCM2025-B/main/data"
FILES = ["附件1.csv", "附件2.csv", "附件3.csv", "附件4.csv"]
OUT_DIR = Path(__file__).resolve().parent.parent / "data"


def fetch(url: str, dest: Path) -> int:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as r:  # noqa: S310
        raw = r.read()
    with open(dest, "wb") as f:
        f.write(raw)
    return len(raw)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = []
    for name in FILES:
        # 使用 percent-encoding 处理中文
        url = f"{BASE}/{quote(name)}"
        out = OUT_DIR / name
        try:
            sz = fetch(url, out)
            print(f"OK  {name}  {sz} bytes -> {out}", flush=True)
        except Exception as exc:  # noqa: BLE001
            buf = io.StringIO()
            print(f"FAIL {name}: {type(exc).__name__}: {exc}", file=buf, flush=True)
            sys.stderr.write(buf.getvalue())
            sys.stderr.flush()
            failures.append(name)
    if failures:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
