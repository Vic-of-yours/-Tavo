#!/usr/bin/env python3
"""Reclassify every selected Aster runtime asset and emit one authoritative catalog.

The migration is deliberately path-only: bytes, public package IDs, item IDs,
semantic keys, CSS variables, and SVG-internal IDs stay stable.  Running the
script again is safe and verifies the already-migrated tree.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
VERSION = "2.0.0"

COMMON = "io.aster.ui.common-assets"
ORBIT = "io.aster.ui.orbit-holo"
WORLD = "io.aster.ui.world-media"

ICONS = (
    "back", "close", "search", "filter", "sort", "add", "more", "dashboard", "map", "location",
    "bag", "quest", "following", "home", "pet", "equipment", "craft", "message", "forum", "live",
    "notification", "data", "resource", "theme", "settings", "lock", "unlock", "edit", "delete",
    "character", "lorebook", "regex", "preset", "image", "audio", "video", "font", "text", "binary",
    "archive", "info", "success", "warning", "error", "codex", "sticker", "gallery", "voice", "music",
    "book", "marker", "developer", "modules", "form", "diagnostics", "parameters", "catalog", "drawer",
    "calendar", "journal",
)

ICON_GROUPS = {
    "nav": {"back", "close", "more", "dashboard", "home", "drawer"},
    "action": {"search", "filter", "sort", "add", "edit", "delete", "lock", "unlock"},
    "status": {"following", "live", "notification", "info", "success", "warning", "error"},
    "world": {"map", "location", "bag", "quest", "pet", "equipment", "craft", "character"},
    "social": {"message", "forum", "sticker", "gallery", "voice", "music"},
    "content": {"data", "resource", "theme", "settings", "lorebook", "regex", "preset", "image", "audio", "video", "font", "text", "binary", "archive", "book", "marker", "calendar", "journal", "catalog"},
    "dev": {"codex", "developer", "modules", "form", "diagnostics", "parameters"},
}


def icon_group(name: str) -> str:
    matches = [group for group, values in ICON_GROUPS.items() if name in values]
    if len(matches) != 1:
        raise RuntimeError(f"icon must have exactly one use group: {name} -> {matches}")
    return matches[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def entry(
    old: str,
    new: str,
    category: str,
    purpose: str,
    package_id: str,
    item_id: str,
    semantic_key: str,
    stored_name: str,
) -> dict[str, str]:
    return {
        "legacyPath": old,
        "path": new,
        "category": category,
        "purpose": purpose,
        "packageId": package_id,
        "itemId": item_id,
        "semanticKey": semantic_key,
        "storedName": stored_name,
    }


def definitions() -> list[dict[str, str]]:
    rows = [
        entry(
            f"ui/common/icons/aster-icon-{name}.svg",
            f"icons/{icon_group(name)}/{name}.svg",
            f"icon-{icon_group(name)}",
            {
                "nav": "导航图标",
                "action": "操作图标",
                "status": "状态反馈图标",
                "world": "世界与玩法图标",
                "social": "社交图标",
                "content": "内容与资源类型图标",
                "dev": "开发工具图标",
            }[icon_group(name)],
            COMMON,
            f"icons-aster-icon-{name}",
            f"icon.{name}",
            f"i-{name}.svg",
        )
        for name in ICONS
    ]
    rows.extend([
        entry("ui/orbit-holo/icons/aster-orbit-icon-team.svg", "icons/hud/team.svg", "hud-icon", "双轨仪表盘队伍图标", ORBIT, "orbit-team", "orbit.team", "hud-team.svg"),
        entry("ui/orbit-holo/icons/aster-orbit-icon-encounter.svg", "icons/hud/encounter.svg", "hud-icon", "双轨仪表盘遭遇图标", ORBIT, "orbit-encounter", "orbit.encounter", "hud-encounter.svg"),
        entry("ui/orbit-holo/icons/aster-orbit-icon-check.svg", "icons/hud/check.svg", "hud-icon", "双轨仪表盘确认图标", ORBIT, "orbit-check", "orbit.check", "hud-check.svg"),
        entry("ui/orbit-holo/icons/aster-orbit-icon-spell.svg", "icons/hud/spell.svg", "hud-icon", "双轨仪表盘法术图标", ORBIT, "orbit-spell", "orbit.spell", "hud-spell.svg"),
        entry("ui/orbit-holo/icons/aster-orbit-icon-map-marker.svg", "icons/hud/marker.svg", "hud-icon", "双轨仪表盘地图标记", ORBIT, "orbit-map-marker", "orbit.map-marker", "hud-marker.svg"),

        entry("ui/common/masks/aster-mask-bracket-button.svg", "masks/bracket.svg", "mask", "括号按钮裁切遮罩", COMMON, "masks-aster-mask-bracket-button", "mask.bracket-button", "mask-bracket.svg"),
        entry("ui/common/masks/aster-mask-chamfer-10.svg", "masks/chamfer-lg.svg", "mask", "大倒角裁切遮罩", COMMON, "masks-aster-mask-chamfer-10", "mask.chamfer-10", "mask-chamfer-lg.svg"),
        entry("ui/common/masks/aster-mask-chamfer-6.svg", "masks/chamfer-sm.svg", "mask", "小倒角裁切遮罩", COMMON, "masks-aster-mask-chamfer-6", "mask.chamfer-6", "mask-chamfer-sm.svg"),
        entry("ui/common/masks/aster-mask-double-notch.svg", "masks/notch.svg", "mask", "双缺口裁切遮罩", COMMON, "masks-aster-mask-double-notch", "mask.double-notch", "mask-notch.svg"),
        entry("ui/common/masks/aster-mask-hex-node.svg", "masks/hex.svg", "mask", "六边节点裁切遮罩", COMMON, "masks-aster-mask-hex-node", "mask.hex-node", "mask-hex.svg"),
        entry("ui/common/masks/aster-mask-tab-slant.svg", "masks/tab.svg", "mask", "斜切标签裁切遮罩", COMMON, "masks-aster-mask-tab-slant", "mask.tab-slant", "mask-tab.svg"),

        entry("ui/common/icons/aster-icons.svg", "sprites/icons.svg", "sprite", "通用图标 SVG 合集", COMMON, "icons-aster-icons", "sprite.icons", "sprite-icons.svg"),
        entry("ui/common/masks/aster-control-masks.svg", "sprites/masks.svg", "sprite", "控件遮罩 SVG 合集", COMMON, "masks-aster-control-masks", "sprite.masks", "sprite-masks.svg"),
        entry("ui/common/decor/aster-decor.svg", "sprites/decor.svg", "sprite", "终端装饰 SVG 合集", COMMON, "decor-aster-decor", "decor.sprite", "sprite-decor.svg"),

        entry("ui/common/textures/texture-noise-256.svg", "textures/noise.svg", "texture", "界面噪点底纹", COMMON, "textures-texture-noise-256", "texture.noise", "tex-noise.svg"),
        entry("ui/common/textures/texture-microgrid-256.svg", "textures/grid.svg", "texture", "界面微网格底纹", COMMON, "textures-texture-microgrid-256", "texture.microgrid", "tex-grid.svg"),
        entry("ui/common/textures/texture-circuit-512.svg", "textures/circuit.svg", "texture", "界面电路底纹", COMMON, "textures-texture-circuit-512", "texture.circuit", "tex-circuit.svg"),
        entry("ui/common/textures/texture-scanline-64.svg", "textures/scan.svg", "texture", "界面扫描线底纹", COMMON, "textures-texture-scanline-64", "texture.scanline", "tex-scan.svg"),

        entry("ui/common/motion/motion-particles.webp", "effects/particles.webp", "effect", "粒子循环动效", COMMON, "motion-motion-particles", "motion.particles", "fx-particles.webp"),
        entry("ui/common/motion/motion-particles-static.png", "effects/particles-still.png", "effect", "粒子动效静态降级图", COMMON, "motion-motion-particles-static", "motion.particles-static", "fx-particles-still.png"),
        entry("ui/common/motion/motion-glitch-scan.webp", "effects/glitch.webp", "effect", "故障扫描循环动效", COMMON, "motion-motion-glitch-scan", "motion.glitch", "fx-glitch.webp"),
        entry("ui/common/motion/motion-glitch-scan-static.png", "effects/glitch-still.png", "effect", "故障扫描静态降级图", COMMON, "motion-motion-glitch-scan-static", "motion.glitch-static", "fx-glitch-still.png"),
        entry("ui/common/motion/motion-pulse-ring.png", "effects/pulse.png", "effect", "脉冲环动效", COMMON, "motion-motion-pulse-ring", "motion.pulse", "fx-pulse.png"),
        entry("ui/common/motion/motion-pulse-ring-static.png", "effects/pulse-still.png", "effect", "脉冲环静态降级图", COMMON, "motion-motion-pulse-ring-static", "motion.pulse-static", "fx-pulse-still.png"),

        entry("ui/common/wallpapers/wallpaper-terminal-cyan.webp", "backgrounds/terminal.webp", "background", "手机终端夜城壁纸", COMMON, "wallpapers-wallpaper-terminal-cyan", "wallpaper.terminal-city", "bg-terminal.webp"),
        entry("ui/common/wallpapers/wallpaper-violet-crystal.webp", "backgrounds/violet.webp", "background", "手机紫晶棱镜壁纸", COMMON, "wallpapers-wallpaper-violet-crystal", "wallpaper.violet-crystal", "bg-violet.webp"),
        entry("ui/common/wallpapers/wallpaper-green-atrium.webp", "backgrounds/atrium.webp", "background", "手机翠色庭院壁纸", COMMON, "wallpapers-wallpaper-green-atrium", "wallpaper.green-atrium", "bg-atrium.webp"),

        entry("ui/orbit-holo/runtime/aster-orbit-city-world-sphere.webp", "scenes/world.webp", "scene", "世界仪表盘透明球体场景", ORBIT, "world-sphere", "world.sphere", "scene-world.webp"),
        entry("ui/orbit-holo/runtime/aster-orbit-home-isometric.webp", "scenes/home.webp", "scene", "世界仪表盘家园场景", ORBIT, "world-home", "world.home", "scene-home.webp"),
        entry("ui/orbit-holo/runtime/social-live-celebration.webp", "scenes/celebration.webp", "scene", "社交直播庆典场景", ORBIT, "social-live-celebration", "social.live.celebration", "scene-celebration.webp"),
        entry("ui/orbit-holo/runtime/social-old-city.webp", "scenes/city.webp", "scene", "社交旧城场景", ORBIT, "social-live-old-city", "social.live.old-city", "scene-city.webp"),
        entry("ui/orbit-holo/runtime/social-north-station.webp", "scenes/station.webp", "scene", "社交北站场景", ORBIT, "social-live-north-station", "social.live.north-station", "scene-station.webp"),
        entry("ui/orbit-holo/runtime/social-home-qa.webp", "scenes/qa.webp", "scene", "社交家园问答场景", ORBIT, "social-live-home-qa", "social.live.home-qa", "scene-qa.webp"),

        entry("ui/world-dashboard/aster-world-map.png", "maps/world.png", "map", "世界缩略地图", WORLD, "world-map", "world.map", "map-world.png"),
    ])
    return rows


def move_exact(source: Path, target: Path) -> None:
    if source.is_file() and target.is_file():
        if source.read_bytes() != target.read_bytes():
            raise RuntimeError(f"asset migration collision: {source} -> {target}")
        source.unlink()
    elif source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        source.replace(target)
    elif not target.is_file():
        raise FileNotFoundError(f"missing old and new asset path: {source} / {target}")


def inspect(path: Path) -> dict[str, object]:
    suffix = path.suffix.lower()
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    detail: dict[str, object] = {"mime": mime}
    if suffix == ".svg":
        root = ET.parse(path).getroot()
        if not root.tag.endswith("svg"):
            raise RuntimeError(f"invalid SVG root: {path}")
        detail["format"] = "SVG"
        if root.attrib.get("viewBox"):
            detail["viewBox"] = root.attrib["viewBox"]
    else:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            detail.update({"format": image.format, "width": image.width, "height": image.height, "mode": image.mode})
    return detail


def remove_empty_legacy_tree() -> None:
    legacy = ASSETS / "ui"
    if not legacy.exists():
        return
    for path in sorted((item for item in legacy.rglob("*") if item.is_dir()), key=lambda item: len(item.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            pass
    try:
        legacy.rmdir()
    except OSError:
        remaining = sorted(path.relative_to(ASSETS).as_posix() for path in legacy.rglob("*") if path.is_file())
        raise RuntimeError(f"unclassified legacy asset files remain: {remaining}")


def write_metadata(rows: list[dict[str, object]]) -> None:
    counts = Counter(str(row["category"]) for row in rows)
    catalog = {
        "schema": "aster.runtime-assets/v2",
        "version": VERSION,
        "status": "classified-and-short-named",
        "policy": {
            "physicalPathsChangedOnly": True,
            "publicPackageIdsPreserved": True,
            "publicItemIdsPreserved": True,
            "semanticKeysPreserved": True,
            "svgInternalIdsPreserved": True,
            "portraitRasterFiles": 0,
        },
        "counts": {"runtimeFiles": len(rows), **dict(sorted(counts.items()))},
        "metadataResource": {
            "packageId": COMMON,
            "itemId": "asset-catalog",
            "semanticKey": "catalog",
            "storedName": "catalog.json",
            "path": "catalog.json",
        },
        "files": rows,
    }
    catalog_path = ASSETS / "catalog.json"
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    checksummed = [ASSETS / str(row["path"]) for row in rows] + [catalog_path]
    (ASSETS / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.relative_to(ASSETS).as_posix()}\n" for path in sorted(checksummed)),
        encoding="utf-8",
    )
    category_lines = "\n".join(f"- `{name}`：{counts[name]} 个" for name in sorted(counts))
    (ASSETS / "README.md").write_text(
        "# Aster 运行素材 r002\n\n"
        "本目录是唯一的现行素材树。94 个视觉文件已按用途分类并改为短路径；文件字节未改动。\n"
        "立绘、头像和人物站姿栅格图为 0。公开 packageId、itemId、语义键、CSS 变量及 SVG 内部 ID 均保持不变。\n\n"
        "## 分类\n\n" + category_lines + "\n\n"
        "`catalog.json` 逐项记录旧路径、新路径、用途、安装短名、字节数和 SHA-256；"
        "`SHA256SUMS.txt` 覆盖 94 个视觉文件及 catalog。\n",
        encoding="utf-8",
    )


def main() -> None:
    rows = definitions()
    if len(rows) != 94:
        raise RuntimeError(f"expected 94 runtime assets, got {len(rows)}")
    for old_metadata in (
        ASSETS / "ui/common/README.md",
        ASSETS / "ui/common/SHA256SUMS.txt",
        ASSETS / "ui/common/asset-catalog.json",
    ):
        if old_metadata.exists():
            old_metadata.unlink()
    for row in rows:
        move_exact(ASSETS / str(row["legacyPath"]), ASSETS / str(row["path"]))
    remove_empty_legacy_tree()

    enriched = []
    for row in rows:
        path = ASSETS / str(row["path"])
        enriched.append({
            **row,
            "assetId": str(row["packageId"]) + ":" + str(row["itemId"]),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "portrait": False,
            **inspect(path),
        })
    for field in ("path", "storedName", "assetId", "semanticKey"):
        values = [str(row[field]) for row in enriched]
        if len(values) != len(set(values)):
            raise RuntimeError(f"duplicate asset {field}")
    digests = [str(row["sha256"]) for row in enriched]
    if len(digests) != len(set(digests)):
        raise RuntimeError("exact duplicate runtime asset content")
    write_metadata(enriched)
    expected = {str(row["path"]) for row in enriched} | {"README.md", "catalog.json", "SHA256SUMS.txt"}
    actual = {path.relative_to(ASSETS).as_posix() for path in ASSETS.rglob("*") if path.is_file()}
    if actual != expected:
        raise RuntimeError(f"asset tree drift: missing={sorted(expected - actual)}, extra={sorted(actual - expected)}")
    print(json.dumps({"ok": True, "runtimeFiles": len(enriched), "metadataFiles": 3, "counts": dict(sorted(Counter(row["category"] for row in enriched).items()))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
