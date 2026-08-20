# Aster 117 Blueprint r001

这是 v117 → Aster 的 B0 冻结工作区。它已经完成来源核验、整文件去重、旧产物隔离、代码/素材双包边界、人物位图清理、86 模块目标架构和七书 172 行迁移映射；尚未宣称 86 模块已实现。

## 当前真值

- 现有可执行源码：36 模块（核心 19 / 功能 5 / 图鉴 1 / 系统 5 / 皮肤 6）。
- 目标架构：86 模块（核心 20 / 功能 28 / 图鉴 12 / 系统 18 / 皮肤 8）。
- v117 完整来源账：172 行；167 `blueprint-mapped`、5 `retired-verified`、0 missing；当前 Aster 实现验收为 0。
- 素材：人物位图为 0；角色槽保留但默认空；图标、SVG、底纹、抽象背景和非人物场景保留。
- 最新包铁律：代码包和素材包各自无整文件重复，跨包也不得共享相同内容。

## 入口

- 总蓝图：`blueprint/ASTER-117-MASTER-BLUEPRINT.md`
- 机器架构：`blueprint/aster-architecture-v1.json`
- 172 行迁移账：`blueprint/v117-to-aster-ledger.json`
- 完整审计：`audit/PROJECT-AUDIT.md`
- Tavo API 审计：`audit/TAVO-API-AUDIT.md`
- 输入来源：`manifests/intake-sources.json`
- 去重/清理账：`manifests/selection-ledger.json`

## 验证与打包

```bash
python3 build_books.py
python3 tools/build_mod_importer_fixture.py
node tests/verify-first-gate.js
node tests/verify-importer.js
node tests/verify-mod-importer.js
node tests/verify-ui-contracts.js
python3 tools/build_blueprint_packages.py
```

浏览器门在可用 Playwright 时运行：

```bash
node tests/verify-browser-ui.js
node tests/verify-mod-importer-browser.js
```

最终只交付 `dist/Aster-117-Blueprint-Code-r001.zip` 与 `dist/Aster-117-Blueprint-Assets-r001.zip`，以及 release/checksum。`out/`、临时报告和历史构建均不提交。

## 下一施工点

从蓝图 B1 `core-20` 开始。第一批先固定可执行代码信任边界与原子 loader，再依次完成 lifecycle、registry/services、schema/store、commands/forms、surfaces/host、assets/imports、renderer/diagnostics/workbenches。不得先造空壳，也不得绕过 172 行账继续修 UI。

远端目标为 `Vic-of-yours/-Tavo` 的 `codex/117-to-aster-blueprint` 分支；本工作区应通过 draft PR 续接，不直接覆盖 `main`。
