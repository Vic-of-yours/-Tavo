#!/usr/bin/env python3
"""Build and verify the deterministic Aster blueprint calibration package."""

from __future__ import annotations

import hashlib
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
OUTPUT = DIST / "Aster-117-Blueprint-Calibration-r002.zip"
FIXED_TIME = (2026, 8, 21, 0, 0, 0)

PAYLOAD = (
    ("blueprint/ASTER-117-CALIBRATION-REGISTER.md", "00-READ-ME-FIRST.md"),
    ("blueprint/ASTER-117-CALIBRATION-DECISIONS.json", "CALIBRATION-DECISIONS.json"),
    ("blueprint/ASTER-117-MASTER-BLUEPRINT.md", "blueprint/ASTER-117-MASTER-BLUEPRINT.md"),
    ("blueprint/aster-architecture-v1.json", "blueprint/aster-architecture-v1.json"),
    ("blueprint/v117-to-aster-ledger.json", "blueprint/v117-to-aster-ledger.json"),
    ("audit/PROJECT-AUDIT.md", "audit/PROJECT-AUDIT.md"),
    ("audit/TAVO-API-AUDIT.md", "audit/TAVO-API-AUDIT.md"),
    ("audit/CODE-PACKAGE-COMPLETENESS-AUDIT.md", "audit/CODE-PACKAGE-COMPLETENESS-AUDIT.md"),
    ("blueprint/ACCEPTANCE.md", "blueprint/ACCEPTANCE.md"),
    ("blueprint/design/orbit/README.md", "blueprint/design/orbit/README.md"),
    ("blueprint/assets/README.md", "blueprint/assets/README.md"),
    ("blueprint/assets/AUDIT.md", "blueprint/assets/AUDIT.md"),
    ("blueprint/assets/ACCEPTANCE.md", "blueprint/assets/ACCEPTANCE.md"),
    ("blueprint/assets/PROVENANCE.md", "blueprint/assets/PROVENANCE.md"),
    ("manifests/intake-sources.json", "manifests/intake-sources.json"),
    ("manifests/selection-ledger.json", "manifests/selection-ledger.json"),
    ("manifests/full-file-disposition.json", "manifests/full-file-disposition.json"),
    ("manifests/GIT-REMOTE-SNAPSHOT.json", "manifests/GIT-REMOTE-SNAPSHOT.json"),
    ("dist/ASTER-117-BLUEPRINT-RELEASE.json", "external-artifacts/ASTER-117-BLUEPRINT-RELEASE.json"),
    ("dist/SHA256SUMS.txt", "external-artifacts/SHA256SUMS.txt"),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    return info


def main() -> None:
    records: list[dict[str, object]] = []
    content_hashes: dict[str, str] = {}
    payload_bytes: dict[str, bytes] = {}

    for source_name, archive_name in PAYLOAD:
        source = ROOT / source_name
        if not source.is_file():
            raise SystemExit(f"missing payload: {source_name}")
        pure = PurePosixPath(archive_name)
        if pure.is_absolute() or ".." in pure.parts:
            raise SystemExit(f"unsafe archive path: {archive_name}")
        data = source.read_bytes()
        digest = sha256(data)
        if digest in content_hashes:
            raise SystemExit(
                f"duplicate payload content: {source_name} == {content_hashes[digest]}"
            )
        content_hashes[digest] = source_name
        payload_bytes[archive_name] = data
        records.append(
            {
                "archivePath": archive_name,
                "sourcePath": source_name,
                "bytes": len(data),
                "sha256": digest,
            }
        )

    architecture = json.loads((ROOT / "blueprint/aster-architecture-v1.json").read_text())
    ledger = json.loads((ROOT / "blueprint/v117-to-aster-ledger.json").read_text())
    remote = json.loads((ROOT / "manifests/GIT-REMOTE-SNAPSHOT.json").read_text())
    decisions = json.loads(
        (ROOT / "blueprint/ASTER-117-CALIBRATION-DECISIONS.json").read_text()
    )
    module_count = sum(len(items) for items in architecture["books"].values())
    if module_count != 86 or architecture["targetExecutableModules"] != 86:
        raise SystemExit("architecture target is not internally consistent at 86")
    if len(ledger["rows"]) != 172 or ledger["counts"]["implementedVerified"] != 0:
        raise SystemExit("migration ledger must remain 172 rows and unimplemented at B0")
    comparison = remote.get("comparison") or {}
    if (
        comparison.get("mismatched") != 0
        or comparison.get("missingRemote") != 0
        or comparison.get("missingLocal") != 0
        or comparison.get("matched") != comparison.get("remoteFiles")
        or comparison.get("matched") != comparison.get("localFiles")
    ):
        raise SystemExit("Git remote snapshot is not a complete byte match")
    if len(decisions["decisions"]) != 30:
        raise SystemExit("calibration decision register must contain CAL-001 through CAL-030")
    if {item["id"] for item in decisions["decisions"]} != {
        f"CAL-{index:03d}" for index in range(1, 31)
    }:
        raise SystemExit("calibration decision IDs are incomplete or duplicated")
    coverage = decisions["architectureCoverageAudit"]
    if (
        coverage["candidateTargetModules"] != 86
        or coverage["directlyTargetedByMigrationRows"] != 65
        or len(coverage["unreferencedTargetModules"]) != 21
    ):
        raise SystemExit("architecture coverage audit must remain 65 direct + 21 open")

    manifest = {
        "schema": "aster.blueprint-calibration-package/v1",
        "version": "calibration-r002",
        "status": "calibration-required-not-implemented",
        "purpose": "Review and revise the r002 blueprint before B1 implementation.",
        "containsCodePackage": False,
        "containsAssetPackage": False,
        "targetExecutableModulesCandidate": 86,
        "migrationRows": 172,
        "implementedVerified": 0,
        "payloadFiles": len(records),
        "duplicatePayloadContentGroups": 0,
        "payload": records,
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()

    DIST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w") as archive:
        for name in sorted(payload_bytes):
            archive.writestr(zip_info(name), payload_bytes[name])
        archive.writestr(zip_info("PACKAGE-MANIFEST.json"), manifest_bytes)

    with zipfile.ZipFile(OUTPUT) as archive:
        if archive.testzip() is not None:
            raise SystemExit("ZIP CRC verification failed")
        names = archive.namelist()
        if len(names) != len(set(names)) or len(names) != len(PAYLOAD) + 1:
            raise SystemExit("ZIP member uniqueness/count verification failed")
        for member in archive.infolist():
            pure = PurePosixPath(member.filename)
            if pure.is_absolute() or ".." in pure.parts or member.is_dir():
                raise SystemExit(f"unsafe or non-file member: {member.filename}")
        embedded = json.loads(archive.read("PACKAGE-MANIFEST.json"))
        for record in embedded["payload"]:
            data = archive.read(record["archivePath"])
            if len(data) != record["bytes"] or sha256(data) != record["sha256"]:
                raise SystemExit(f"manifest mismatch: {record['archivePath']}")

    digest = sha256(OUTPUT.read_bytes())
    print(
        json.dumps(
            {
                "file": OUTPUT.name,
                "bytes": OUTPUT.stat().st_size,
                "sha256": digest,
                "members": len(PAYLOAD) + 1,
                "duplicatePayloadContentGroups": 0,
                "crc": "pass",
                "status": "calibration-required-not-implemented",
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
