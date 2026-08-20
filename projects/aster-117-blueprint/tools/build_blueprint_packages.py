#!/usr/bin/env python3
"""Validate and build the two deterministic 117→Aster blueprint packages."""

from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
VERSION = "r002"
STAMP = (2026, 8, 21, 0, 0, 0)
CODE_NAME = f"Aster-117-Blueprint-Code-{VERSION}.zip"
ASSET_NAME = f"Aster-117-Blueprint-Assets-{VERSION}.zip"

EXCLUDED_PARTS = {".git", "dist", "out", "__pycache__"}
BLOCKED_RASTER_TOKENS = (
    "player-standing",
    "player-open",
    "character-standing",
    "portrait",
)
RASTER_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif", ".bmp"}
ARCHIVE_SUFFIXES = {".zip", ".tpg", ".tar", ".gz", ".7z", ".rar"}


def digest_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def source_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if relative.parts[:1] == ("reports",):
            continue
        files.append(path)
    return sorted(files)


def rows_for(paths: list[Path], base: Path = ROOT) -> list[dict[str, object]]:
    rows = []
    for path in paths:
        relative = path.relative_to(base).as_posix()
        rows.append({
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": digest_file(path),
        })
    return rows


def assert_unique_content(paths: list[Path], label: str) -> None:
    by_digest: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        by_digest[digest_file(path)].append(path.relative_to(ROOT).as_posix())
    duplicates = {key: value for key, value in by_digest.items() if len(value) > 1}
    if duplicates:
        raise RuntimeError(f"{label} contains exact duplicate content: {duplicates}")


def verify_asset_catalog() -> dict[str, object]:
    root = ROOT / "assets"
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    if catalog.get("schema") != "aster.runtime-assets/v2" or catalog.get("version") != "2.0.0":
        raise RuntimeError("unexpected unified asset catalog schema/version")
    rows = catalog.get("files") or []
    expected = {str(row["path"]): row for row in rows}
    actual = {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and path.name not in {"README.md", "SHA256SUMS.txt", "catalog.json"}
    }
    if set(expected) != set(actual):
        raise RuntimeError("unified asset catalog path set drift")
    if len(rows) != 94:
        raise RuntimeError(f"unified asset catalog must contain 94 runtime files, got {len(rows)}")
    for field in ("path", "legacyPath", "storedName", "assetId", "semanticKey"):
        values = [str(row[field]) for row in rows]
        if len(values) != len(set(values)):
            raise RuntimeError(f"duplicate catalog {field}")
    for relative, path in actual.items():
        row = expected[relative]
        if path.stat().st_size != int(row["bytes"]) or digest_file(path) != row["sha256"]:
            raise RuntimeError(f"asset catalog hash drift: {relative}")
        if row.get("portrait") is not False:
            raise RuntimeError(f"asset lacks explicit non-portrait classification: {relative}")
        suffix = path.suffix.lower()
        if suffix in RASTER_SUFFIXES:
            with Image.open(path) as image:
                if int(row.get("width", -1)) != image.width or int(row.get("height", -1)) != image.height or row.get("format") != image.format:
                    raise RuntimeError(f"asset catalog raster metadata drift: {relative}")
        elif suffix == ".svg":
            svg_root = ET.parse(path).getroot()
            if not svg_root.tag.endswith("svg"):
                raise RuntimeError(f"invalid SVG root: {relative}")
            ids = {node.attrib["id"] for node in svg_root.iter() if node.attrib.get("id")}
            for attribute in ("href", "{http://www.w3.org/1999/xlink}href"):
                for node in svg_root.iter():
                    value = node.attrib.get(attribute, "")
                    if value.startswith("#") and value[1:] not in ids:
                        raise RuntimeError(f"unresolved SVG href in {relative}: {value}")
            for node in svg_root.iter():
                for value in node.attrib.values():
                    for reference in re.findall(r"url\(#([^)]+)\)", value):
                        if reference not in ids:
                            raise RuntimeError(f"unresolved SVG url() in {relative}: {reference}")

    checksum_rows = {}
    for line in (root / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        checksum_rows[relative] = digest
    expected_checksum_paths = set(actual) | {"catalog.json"}
    if set(checksum_rows) != expected_checksum_paths:
        raise RuntimeError("asset SHA256SUMS path set drift")
    for relative, expected_digest in checksum_rows.items():
        if digest_file(root / relative) != expected_digest:
            raise RuntimeError(f"asset SHA256SUMS drift: {relative}")

    common_text = (ROOT / "src-modules/func/517-common-ui-assets.txt").read_text(encoding="utf-8")
    orbit_text = (ROOT / "src-modules/func/518-orbit-holo-assets.txt").read_text(encoding="utf-8")
    preference_text = (ROOT / "src-modules/skin/12-preference-registry.txt").read_text(encoding="utf-8")
    runtime_text = "\n".join((common_text, orbit_text, preference_text))
    icon_rows = [row for row in rows if str(row["semanticKey"]).startswith("icon.")]
    icon_names = re.search(r"var ICONS = \[(.*?)\];", common_text, re.DOTALL)
    if not icon_names:
        raise RuntimeError("common icon registry is missing")
    registered_icons = re.findall(r"'([^']+)'", icon_names.group(1))
    if set(registered_icons) != {str(row["semanticKey"]).removeprefix("icon.") for row in icon_rows}:
        raise RuntimeError("common icon registry/catalog drift")
    if "'i-' + name + '.svg'" not in common_text:
        raise RuntimeError("common icon short stored-name rule drift")
    for row in rows:
        if str(row["semanticKey"]).startswith("icon."):
            continue
        if str(row["storedName"]) not in runtime_text or str(row["semanticKey"]) not in runtime_text:
            raise RuntimeError(f"asset is not registered by semantic key and short name: {row['path']}")
    metadata = catalog.get("metadataResource") or {}
    if str(metadata.get("storedName")) not in common_text or str(metadata.get("itemId")) not in common_text:
        raise RuntimeError("catalog metadata resource registry drift")
    return {"runtimeFiles": len(rows), "portraitRasterFiles": 0, "catalogVersion": catalog["version"]}


def verify_assets(asset_paths: list[Path]) -> dict[str, object]:
    catalog_validation = verify_asset_catalog()
    counts = Counter()
    dimensions = []
    for path in asset_paths:
        relative = path.relative_to(ROOT).as_posix()
        suffix = path.suffix.lower()
        if suffix in ARCHIVE_SUFFIXES:
            raise RuntimeError(f"nested archive is forbidden in asset source: {relative}")
        if suffix in RASTER_SUFFIXES:
            lower = relative.lower()
            if any(token in lower for token in BLOCKED_RASTER_TOKENS):
                raise RuntimeError(f"portrait-like raster path is forbidden: {relative}")
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                dimensions.append({"path": relative, "width": image.width, "height": image.height, "format": image.format})
            counts["raster"] += 1
        elif suffix == ".svg":
            root = ET.parse(path).getroot()
            if not root.tag.endswith("svg"):
                raise RuntimeError(f"invalid SVG root: {relative}")
            counts["svg"] += 1
        elif suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            counts["json"] += 1
        else:
            counts["metadata"] += 1
    return {"counts": dict(sorted(counts.items())), "dimensions": dimensions, **catalog_validation}


def verify_code(code_paths: list[Path]) -> dict[str, object]:
    blocked = re.compile(
        r"aster-orbit-player-open|aster-player-standing|aster-player-open-v2-source|"
        r"io\.aster\.ui\.world-media:home-isometric|player\.open|--aster-orbit-player"
    )
    hits = []
    for path in code_paths:
        relative_parts = path.relative_to(ROOT).parts
        if relative_parts[:1] not in {("src-modules",), ("plugin-runtime",), ("plugin-mod-importer",), ("tests",)}:
            continue
        if path.suffix.lower() not in {".md", ".txt", ".js", ".json", ".py", ".html"}:
            continue
        text = path.read_text(encoding="utf-8")
        if blocked.search(text):
            hits.append(path.relative_to(ROOT).as_posix())
        if path.suffix.lower() == ".json":
            json.loads(text)
    if hits:
        raise RuntimeError(f"removed portrait asset references remain: {hits}")

    module_paths = sorted((ROOT / "src-modules").rglob("*.txt"))
    ids = []
    for path in module_paths:
        match = re.search(r"^@id\s+(.+)$", path.read_text(encoding="utf-8"), re.MULTILINE)
        if not match:
            raise RuntimeError(f"module without @id: {path.relative_to(ROOT)}")
        ids.append(match.group(1).strip())
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate Aster module id")
    domains = Counter(path.parent.name for path in module_paths)
    return {"modules": len(module_paths), "domains": dict(sorted(domains.items()))}


def write_zip(target: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name])


def verify_zip(target: Path) -> dict[str, object]:
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"CRC failure in {target.name}: {bad}")
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate ZIP member path in {target.name}")
        digests = [digest_bytes(archive.read(name)) for name in names]
        if len(digests) != len(set(digests)):
            raise RuntimeError(f"exact duplicate member content in {target.name}")
        return {"members": len(names), "bytes": target.stat().st_size, "sha256": digest_file(target)}


def main() -> None:
    paths = source_files()
    asset_paths = [path for path in paths if path.relative_to(ROOT).parts[:1] == ("assets",)]
    code_paths = [path for path in paths if path not in asset_paths]
    assert_unique_content(paths, "curated workspace")
    asset_validation = verify_assets(asset_paths)
    code_validation = verify_code(code_paths)

    code_rows = rows_for(code_paths)
    asset_rows = rows_for(asset_paths, ROOT / "assets")
    code_manifest = {
        "schema": "aster.blueprint-code-package/v1",
        "version": VERSION,
        "boundary": "code-and-blueprint; no runtime assets",
        "files": code_rows,
    }
    asset_manifest = {
        "schema": "aster.blueprint-asset-package/v1",
        "version": VERSION,
        "boundary": "runtime icons, masks, textures, backgrounds and scenes; no portrait raster",
        "validation": asset_validation,
        "files": asset_rows,
    }

    code_members = {path.relative_to(ROOT).as_posix(): path.read_bytes() for path in code_paths}
    asset_members = {path.relative_to(ROOT / "assets").as_posix(): path.read_bytes() for path in asset_paths}
    code_members["CODE-PACKAGE-MANIFEST.json"] = json_bytes(code_manifest)
    asset_members["ASSET-PACKAGE-MANIFEST.json"] = json_bytes(asset_manifest)

    code_member_digests = {digest_bytes(value) for value in code_members.values()}
    asset_member_digests = {digest_bytes(value) for value in asset_members.values()}
    overlap = code_member_digests & asset_member_digests
    if overlap:
        raise RuntimeError(f"code/asset packages share exact member content: {sorted(overlap)}")

    DIST.mkdir(parents=True, exist_ok=True)
    code_target = DIST / CODE_NAME
    asset_target = DIST / ASSET_NAME
    write_zip(code_target, code_members)
    write_zip(asset_target, asset_members)
    result = {
        "schema": "aster.blueprint-release/v1",
        "version": VERSION,
        "workspace": {
            "files": len(paths),
            "bytes": sum(path.stat().st_size for path in paths),
            "duplicateContentGroups": 0,
            "portraitRasterFiles": asset_validation["portraitRasterFiles"],
        },
        "code": {**verify_zip(code_target), "file": CODE_NAME, **code_validation},
        "assets": {**verify_zip(asset_target), "file": ASSET_NAME, **asset_validation["counts"]},
        "crossPackageDuplicateMembers": 0,
    }
    release_path = DIST / "ASTER-117-BLUEPRINT-RELEASE.json"
    release_path.write_bytes(json_bytes(result))
    checksum_path = DIST / "SHA256SUMS.txt"
    checksum_path.write_text(
        "".join(f"{digest_file(path)}  {path.name}\n" for path in (code_target, asset_target, release_path)),
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
