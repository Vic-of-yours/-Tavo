#!/usr/bin/env python3
"""Verify the current code and asset packages from clean extraction roots."""

from __future__ import annotations

import hashlib
import json
import stat
import tempfile
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def validate_path(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name:
        raise RuntimeError(f"unsafe archive member: {name}")


def verify_package(path: Path, manifest_name: str) -> tuple[set[str], dict[str, object]]:
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"CRC failure: {path.name}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate member path: {path.name}")
        for info in archive.infolist():
            validate_path(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise RuntimeError(f"symlink member: {info.filename}")
        if manifest_name not in names:
            raise RuntimeError(f"missing package manifest: {path.name}")
        manifest = json.loads(archive.read(manifest_name))
        expected = {row["path"]: row for row in manifest.get("files") or []}
        actual = set(names) - {manifest_name}
        if set(expected) != actual:
            raise RuntimeError(f"manifest member set mismatch: {path.name}")
        digests = set()
        for name in names:
            content = archive.read(name)
            digest = sha256(content)
            if digest in digests:
                raise RuntimeError(f"duplicate member content: {path.name}:{name}")
            digests.add(digest)
            if name in expected:
                row = expected[name]
                if len(content) != int(row["bytes"]) or digest != row["sha256"]:
                    raise RuntimeError(f"manifest hash mismatch: {path.name}:{name}")
        REPORTS.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="aster-release-", dir=REPORTS) as temporary:
            archive.extractall(temporary)
            extracted = sorted(p for p in Path(temporary).rglob("*") if p.is_file())
            if len(extracted) != len(names):
                raise RuntimeError(f"clean extraction file count mismatch: {path.name}")
        return digests, {"file": path.name, "members": len(names), "sha256": sha256(path.read_bytes())}


def main() -> None:
    release = json.loads((DIST / "ASTER-117-BLUEPRINT-RELEASE.json").read_text(encoding="utf-8"))
    code = DIST / str(release["code"]["file"])
    assets = DIST / str(release["assets"]["file"])
    code_digests, code_result = verify_package(code, "CODE-PACKAGE-MANIFEST.json")
    asset_digests, asset_result = verify_package(assets, "ASSET-PACKAGE-MANIFEST.json")
    if code_digests & asset_digests:
        raise RuntimeError("code and asset packages share exact member content")
    if code_result["sha256"] != release["code"]["sha256"] or asset_result["sha256"] != release["assets"]["sha256"]:
        raise RuntimeError("release manifest package hash mismatch")
    checksum_rows = {}
    for line in (DIST / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split("  ", 1)
        checksum_rows[name] = digest
    for path in (code, assets, DIST / "ASTER-117-BLUEPRINT-RELEASE.json"):
        if checksum_rows.get(path.name) != sha256(path.read_bytes()):
            raise RuntimeError(f"external checksum mismatch: {path.name}")
    print(json.dumps({
        "ok": True,
        "cleanExtraction": True,
        "code": code_result,
        "assets": asset_result,
        "crossPackageDuplicateMembers": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
