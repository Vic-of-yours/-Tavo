# Aster 117 Blueprint r002

这是 v117 → Aster 的蓝图校准候选工作区，不是“设计已经最终冻结”的声明。r002 完成来源逐文件处置、代码/素材双包边界、94 个视觉素材用途分类与短名化、人物位图清理、86 模块候选架构和七书 172 行迁移映射；尚未宣称 86 模块已获用户批准或已经实现。

## 当前真值

- 现有可执行源码：36 模块（核心 19 / 功能 5 / 图鉴 1 / 系统 5 / 皮肤 6）。
- 目标架构：86 模块（核心 20 / 功能 28 / 图鉴 12 / 系统 18 / 皮肤 8）。
- v117 完整来源账：172 行；167 `blueprint-mapped`、5 `retired-verified`、0 missing；当前 Aster 实现验收为 0。
- 素材：94 个视觉文件（78 SVG / 16 栅格）按 15 个用途类别存放；人物位图为 0；角色槽保留但默认空。
- 最新包铁律：清理后当前树的每个文件必须进入 Code 或 Assets r002；精确重复会让构建直接失败，不会静默吞掉文件。
- 来源边界：历史、vendor、生成物、参考件和已剔除人物素材不嵌入当前包，但每个文件表示都在完整处置账中有唯一决定。

## 入口

- 总蓝图：`blueprint/ASTER-117-MASTER-BLUEPRINT.md`
- 机器架构：`blueprint/aster-architecture-v1.json`
- 172 行迁移账：`blueprint/v117-to-aster-ledger.json`
- 完整审计：`audit/PROJECT-AUDIT.md`
- Tavo API 审计：`audit/TAVO-API-AUDIT.md`
- 输入来源：`manifests/intake-sources.json`
- 去重/清理账：`manifests/selection-ledger.json`
- 全输入逐文件处置账：`manifests/full-file-disposition.json`
- 代码包完整性审计：`audit/CODE-PACKAGE-COMPLETENESS-AUDIT.md`
- 素材分类真源：`assets/catalog.json`
- 蓝图放行矩阵：`blueprint/ACCEPTANCE.md`

## 验证与打包

```bash
python3 build_books.py
python3 tools/build_mod_importer_fixture.py
node tests/verify-first-gate.js
node tests/verify-importer.js
node tests/verify-mod-importer.js
node tests/verify-ui-contracts.js
python3 tools/verify_assets.py
python3 tools/build_blueprint_packages.py
python3 tools/verify_blueprint_release.py
```

浏览器门在可用 Playwright 时运行：

```bash
node tests/verify-browser-ui.js
node tests/verify-mod-importer-browser.js
```

最终交付 `dist/Aster-117-Blueprint-Code-r002.zip` 与 `dist/Aster-117-Blueprint-Assets-r002.zip`，以及 release/checksum。素材 ZIP 是可审计源包，不冒充可直接安装的 `aster.mod/v1`。`out/`、临时报告和历史构建均不进入最新包。

## 下一校准点

先共同确认 83/86 模块边界、21 个无 v117 direct target 的目标模块、loader 信任方案、逐模块合同与 UI/参数验收轨，再进入 B1。不得把 `implementedVerified=0` 或浏览器/Tavo `PENDING` 描述成完成。

远端目标为 `Vic-of-yours/-Tavo` 的 `codex/117-to-aster-blueprint` 分支；本工作区通过 draft PR 续接，不直接覆盖 `main`。Git 完整性只按远端实际提交内容表述，不能用附件 SHA 代替可恢复的原始历史字节。
