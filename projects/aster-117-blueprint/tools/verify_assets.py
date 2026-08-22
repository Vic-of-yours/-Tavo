#!/usr/bin/env python3
"""Run the standalone r002 asset/catalog/registry validation gate."""

from __future__ import annotations

import json

from build_blueprint_packages import ROOT, source_files, verify_assets


def main() -> None:
    paths = source_files()
    assets = [path for path in paths if path.relative_to(ROOT).parts[:1] == ("assets",)]
    result = verify_assets(assets)
    print(json.dumps({"ok": True, **result}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
