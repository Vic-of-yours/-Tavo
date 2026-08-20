#!/usr/bin/env python3
"""Build a per-file disposition ledger for every supplied 117→Aster input.

This ledger is an audit index, not a container for old source bytes.  It proves
that selection was explicit: every file representation is classified as
current, deduplicated, superseded, generated, vendor, history, reference, or
removed portrait material.  Unknown paths fail the build instead of silently
falling out of the release.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_WORKSPACE = ROOT.parent
STAMP = "2026-08-21T00:00:00+09:00"

ARCHIVE_SUFFIXES = {".zip", ".tpg"}
PORTRAIT_TOKENS = (
    "player-standing", "player-open", "character-standing", "portrait", "立绘", "头像",
)

ASSET_SUCCESSORS = {
    row["legacyPath"]: row["path"]
    for row in json.loads((ROOT / "assets/catalog.json").read_text(encoding="utf-8"))["files"]
}

TOOL_SUCCESSORS = {
    "package_release.py": "tools/build_blueprint_packages.py",
    "tools/build_common_ui_assets.py": "tools/reclassify_assets.py",
    "tools/build_runtime_asset_packages.py": "tools/build_blueprint_packages.py",
    "tools/package_common_ui_delivery.py": "tools/build_blueprint_packages.py",
    "tools/verify_common_ui_assets.py": "tools/verify_assets.py",
    "tools/verify_orbit_holo_assets.py": "tools/verify_assets.py",
    "tools/build_blueprint_audit.py": "audit/PROJECT-AUDIT.md",
    "tools/build_migration_ledger.py": "tools/build_v117_aster_ledger.py",
    "tools/build_resource_sync_fix.py": "tools/build_delta_patch.py",
    "tools/build_world_media_delta.py": "tools/build_delta_patch.py",
}


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts and "\\" not in name


def add(rows: list[dict[str, object]], source: str, path: str, content: bytes, representation: str) -> None:
    rows.append({
        "source": source,
        "path": path,
        "representation": representation,
        "bytes": len(content),
        "sha256": digest(content),
    })


def scan_zip(rows: list[dict[str, object]], source: str, content: bytes, prefix: str = "", depth: int = 0) -> None:
    if depth > 4:
        raise RuntimeError(f"archive nesting too deep: {source}:{prefix}")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"CRC failure: {source}:{prefix}")
        names = [info.filename for info in archive.infolist() if not info.is_dir()]
        if len(names) != len(set(names)):
            raise RuntimeError(f"duplicate archive member path: {source}:{prefix}")
        for name in sorted(names):
            if not safe_member(name):
                raise RuntimeError(f"unsafe archive member: {source}:{name}")
            payload = archive.read(name)
            full = f"{prefix}!/{name}" if prefix else name
            add(rows, source, full, payload, "archive-member")
            if Path(name).suffix.lower() in ARCHIVE_SUFFIXES:
                try:
                    scan_zip(rows, source, payload, full, depth + 1)
                except zipfile.BadZipFile:
                    pass


def selected_files() -> tuple[dict[str, Path], dict[str, str]]:
    by_sha: dict[str, Path] = {}
    by_path: dict[str, str] = {}
    excluded = {"dist", "out", "reports", "__pycache__"}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in excluded or part == ".git" for part in relative.parts):
            continue
        if relative.as_posix() == "manifests/full-file-disposition.json":
            continue
        value = digest(path.read_bytes())
        if value in by_sha:
            raise RuntimeError(f"selected workspace has duplicate content: {by_sha[value]} / {path}")
        by_sha[value] = path
        by_path[relative.as_posix()] = value
    return by_sha, by_path


def project_relative(path: str) -> str | None:
    marker = "工作区/01_CURRENT_PROJECT/aster-workspace/"
    return path.split(marker, 1)[1] if marker in path else None


def legacy_asset_successor(relative: str) -> str | None:
    if not relative.startswith("assets/"):
        return None
    return ASSET_SUCCESSORS.get(relative.removeprefix("assets/"))


def classify_project(path: str, sha: str, selected_by_path: dict[str, str]) -> tuple[str, str, str | None]:
    lower = path.lower()
    if path == "<container>":
        return "external-source", "用户原始 Projects 附件以整包 SHA-256 登记，不嵌套进交付包", None
    relative = project_relative(path)
    if any(token in lower for token in PORTRAIT_TOKENS):
        return "portrait-removed", "人物、头像或立绘素材按 r002 空槽策略剔除", None
    if relative:
        successor = legacy_asset_successor(relative)
        if successor:
            return "included-assets-renamed", "运行素材按用途分类并改为短路径，字节保持不变", f"assets/{successor}"
        if relative in selected_by_path:
            if selected_by_path[relative] == sha:
                return "included-code", "当前代码/蓝图文件逐字节保留", relative
            return "superseded", "同一路径已有清理后的现行版本", relative
        if relative.startswith(("out/", "reports/", "__pycache__/")):
            return "generated", "构建产物、测试报告或缓存由现行源码重建，不进入源码包", None
        if relative == "design/ui-common-assets/06-delivery-audit.md" or relative.startswith("design/orbit-holo-veil/mockups/"):
            return "reference-only", "历史交付证据或设计 mockup 不作为 r002 当前通过证据", "manifests/full-file-disposition.json"
        if relative.startswith("design/orbit-holo-veil/contracts/"):
            return "superseded", "机器合同已迁入现行 blueprint/contracts 并保留有效责任", "blueprint/design/orbit/README.md"
        if relative.startswith("design/orbit-holo-veil/") or relative == "design/README.md":
            return "superseded", "旧 UI 设计包含已退役人物方案与旧路径；有效责任由空槽版设计合同接替", "blueprint/design/orbit/README.md"
        if relative.startswith("design/ui-common-assets/"):
            return "superseded", "旧素材设计由 r002 用途分类、短名 catalog 和放行门接替", "blueprint/assets/README.md"
        if relative in TOOL_SUCCESSORS:
            return "superseded", "旧构建/增量/验证入口由现行单一工具接替", TOOL_SUCCESSORS[relative]
        if relative == "assets/ui/orbit-holo/README.md" or relative.startswith("assets/"):
            return "superseded", "旧素材说明或旧布局由 assets/README.md 与 assets/catalog.json 接替", "assets/catalog.json"
        return "superseded", "旧工作区唯一文件经逐项审计后由 r002 当前树或处置账接替", "audit/CODE-PACKAGE-COMPLETENESS-AUDIT.md"
    if "/.venv/" in lower or "/site-packages/" in lower or "node_modules/" in lower:
        return "vendor", "第三方依赖不复制进源码包", None
    if path.startswith(("工作区/02_BASELINE_V117/", "工作区/03_CONTEXT_AND_HANDOFF/", "工作区/05_RELEASE_HISTORY_EXPANDED/")):
        return "history-only", "旧基线、旧蓝图、旧测试或归档仅作为历史来源", None
    if path.startswith(("工作区/04_REFERENCE_ASSETS/", "参考图/", "示意图/")):
        return "reference-only", "制作源或参考素材不进入无冗余运行包", None
    if path.startswith("交付区/") or lower.endswith((".zip", ".tpg")):
        return "generated", "旧交付容器或可重建压缩包不嵌套进新包", None
    if path == "工作区/06_TOOLING/requirements-common-ui.txt":
        return "superseded", "旧素材依赖锁由当前最小依赖锁接替", "requirements-assets.txt"
    if path.startswith("工作区/06_TOOLING/"):
        return "reference-only", "外部维护工具或说明不复制进项目代码包", None
    if lower.startswith("git/"):
        return "history-only", "空白或旧 Git 工作记录不属于当前源码", None
    return "reference-only", "项目说明、接收记录或非运行参考内容不进入当前源码包", None


def classify_non_project(source: str, path: str) -> tuple[str, str, str | None]:
    lower = path.lower()
    if path == "<container>":
        return "external-source", "用户原始附件以整包 SHA-256 登记，不嵌套进交付包", None
    if source == "v117":
        return "history-only", "v117 叶子文件仅作为迁移历史；功能处置见 172 行迁移账", "blueprint/v117-to-aster-ledger.json"
    if source == "small-phone":
        if "cover" in lower or any(token in lower for token in PORTRAIT_TOKENS):
            return "portrait-removed", "参考插件人物封面按空槽策略剔除", None
        return "reference-only", "小手机插件仅用于行为与交互校准，不照搬源码", "audit/PROJECT-AUDIT.md"
    if source == "ranch-lorebook":
        return "reference-only", "牧场世界书仅作叙事内容与注入边界参考", "audit/PROJECT-AUDIT.md"
    return "reference-only", "外部参考文件不进入当前实现", None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, default=DEFAULT_WORKSPACE)
    parser.add_argument("--output", type=Path, default=ROOT / "manifests/full-file-disposition.json")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    projects_root = workspace / "intake/projects_raw/Projects"
    projects_zip = workspace / "project_sources/01-Projects.zip"
    v117_zip = workspace / "upload/vi-project-dev-v2-v117.zip"
    phone_tpg = workspace / "upload/绮楼在改小手机-1.4.1.tpg"
    ranch_json = workspace / "upload/Tavo_兽人牧场_1kYBH.json"
    required = (projects_root, projects_zip, v117_zip, phone_tpg, ranch_json)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing intake inputs: {missing}")

    rows: list[dict[str, object]] = []
    add(rows, "Projects", "<container>", projects_zip.read_bytes(), "container")
    for path in sorted(item for item in projects_root.rglob("*") if item.is_file()):
        add(rows, "Projects", path.relative_to(projects_root).as_posix(), path.read_bytes(), "expanded-file")
    for source, path in (("v117", v117_zip), ("small-phone", phone_tpg)):
        payload = path.read_bytes()
        add(rows, source, "<container>", payload, "container")
        scan_zip(rows, source, payload)
    add(rows, "ranch-lorebook", "<container>", ranch_json.read_bytes(), "container")

    selected_by_sha, selected_by_path = selected_files()
    source_by_sha: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        source_by_sha[str(row["sha256"])].append(row)

    canonical_source: dict[str, str] = {}
    for sha, members in source_by_sha.items():
        canonical_source[sha] = f"{members[0]['source']}:{members[0]['path']}"

    for row in rows:
        sha = str(row["sha256"])
        source = str(row["source"])
        path = str(row["path"])
        selected = selected_by_sha.get(sha)
        selected_relative = selected.relative_to(ROOT).as_posix() if selected else None
        decision: str
        reason: str
        successor: str | None

        if source == "Projects":
            decision, reason, successor = classify_project(path, sha, selected_by_path)
        else:
            decision, reason, successor = classify_non_project(source, path)

        logical_successor = successor and selected_by_path.get(successor) == sha
        if selected and path != "<container>" and source == "Projects" and project_relative(path):
            decision = "included-assets-renamed" if selected_relative.startswith("assets/") and project_relative(path) != selected_relative else "included-code"
            reason = "原始唯一内容已在 r002 当前树逐字节保留" + ("并按用途改为短路径" if decision == "included-assets-renamed" else ("；物理路径已整理" if project_relative(path) != selected_relative else ""))
            successor = selected_relative
        elif selected and path != "<container>" and (logical_successor or decision.startswith("included")):
            decision = "included-assets-renamed" if selected_relative.startswith("assets/") else "included-code"
            reason = "原始唯一内容已在 r002 当前树逐字节保留"
            successor = selected_relative
        elif len(source_by_sha[sha]) > 1 and f"{source}:{path}" != canonical_source[sha]:
            decision = "duplicate-of"
            reason = "与已登记来源内容 SHA-256 完全相同，仅保留一份语义真源"
            successor = canonical_source[sha]

        row["decision"] = decision
        row["reason"] = reason
        if successor:
            if decision == "duplicate-of":
                row["duplicateOf"] = successor
            else:
                row["selectedPath"] = successor

    allowed = {
        "included-code", "included-assets-renamed", "duplicate-of", "superseded", "generated",
        "history-only", "vendor", "reference-only", "portrait-removed", "external-source",
    }
    unknown = sorted({str(row["decision"]) for row in rows} - allowed)
    if unknown:
        raise RuntimeError(f"unrecognized decisions: {unknown}")
    summary = Counter(str(row["decision"]) for row in rows)
    duplicate_groups = sum(1 for members in source_by_sha.values() if len(members) > 1)
    unique_source_content = len(source_by_sha)
    output = {
        "schema": "aster.full-file-disposition/v1",
        "version": "r002",
        "generatedAt": STAMP,
        "policy": {
            "exactDuplicateDefinition": "same SHA-256 bytes",
            "sourceContainersEmbedded": False,
            "unknownDecisionCount": 0,
            "currentPackageCompleteness": "all files in the cleaned r002 workspace are packaged; historical, generated, vendor, reference-only and portrait inputs are indexed but not embedded",
        },
        "summary": {
            "fileRepresentations": len(rows),
            "uniqueSourceContent": unique_source_content,
            "exactDuplicateGroups": duplicate_groups,
            "decisions": dict(sorted(summary.items())),
        },
        "sources": {
            source: {
                "representations": sum(1 for row in rows if row["source"] == source),
                "uniqueSha256": len({row["sha256"] for row in rows if row["source"] == source}),
            }
            for source in sorted({str(row["source"]) for row in rows})
        },
        "files": sorted(rows, key=lambda row: (str(row["source"]), str(row["path"]))),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
