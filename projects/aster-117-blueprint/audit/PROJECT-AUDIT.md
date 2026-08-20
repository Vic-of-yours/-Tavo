# 117 → Aster 完整项目审计

> r002 更新（2026-08-21）：本文主体保留接收阶段的 r001 审计证据；最新操作口径以 `audit/CODE-PACKAGE-COMPLETENESS-AUDIT.md`、`manifests/full-file-disposition.json` 和 `assets/catalog.json` 为准。r002 清理树为 193 个源文件（Code 96 / Assets 97），94 个视觉文件完成用途分类与短名化，视觉哈希集合相对 r001 为 94/94 相同；双包精确重复和跨包重复均为 0。86 模块是待用户校准的候选值，不再使用“B0 冻结”表示最终批准。

审计基线：2026-08-20  
交付状态：B0 蓝图冻结；不是 86 模块实现完成声明  
铁律：最新工作树与两个交付包不得出现整文件内容重复；旧版本、构建物和历史报告只留 Git 历史，不进入最新包。

## 1. 审计结论

1. 四个输入均完成只读结构、CRC/JSON、路径安全和 SHA-256 检查，没有执行参考包代码。
2. `Projects.zip` 不能直接作为最新版：展开 2,381 个文件，32 个精确重复组、61 份冗余副本，可回收 20,254,991 B；还存在两个整包级逻辑复制。
3. v117 递归展开后的 256 个叶子文件只有 248 份唯一内容，8 组精确重复、72,859 B 冗余；外层 importer 1.0.4 已被 1.0.5 明确取代。
4. 当前 Aster 0.9 有 36 个真实可执行模块和一套可运行 UI/工具实现，但其旧 149 行迁移账只有 2 verified、29 partial、118 pending，不能作为 117 完成版。
5. 小手机参考包没有整文件重复，却有显著的跨面板复制；其唯一图片是扩展名伪装为 JPG 的人物 PNG，且代码/API/权限模型不能直接移植。
6. 牧场世界书 8 条内容均唯一，但 7 条常驻正文占 165,640 字符（93.0%）；应拆成索引、检索与分块注入，不得全文常驻。
7. Tavo 基础 API 调用面大体合规；动态执行世界书代码、远程字体权限、实体预检和缺失的 EJS/预设叙事链仍是蓝图阻断项。
8. 合流目标不是 36+83，而是 86 个唯一职责模块；完整来源口径为七书 172 行，另设两个插件行为轨。
9. r001 已剔除四份人物位图及全部旧构建/历史容器；`player.avatar`、`player.standing`、`social.portrait` 只保留默认空的语义槽。

## 2. 输入指纹与来源裁定

| 输入 | 大小 | SHA-256 | 来源结论 | 用途 |
|---|---:|---|---|---|
| `Projects.zip` | 111,563,600 B | `213680352f1d9db96f42bce2425d3ffc74ddd9b7d36031f537015c9b2d90f8c9` | 用户交接包；包内 Git 为 0 commit/0 remote，不能证明历史 | Aster 0.9 实现、历史、工具与视觉证据 |
| `vi-project-dev-v2-v117.zip` | 2,091,251 B | `7cf04ac30f641a70656eff9ecd43e854e45b87ac35de742681e06f7f5064e631` | 用户原件；无 repo URL/commit/license | 行为与七书迁移真源 |
| `绮楼在改小手机-1.4.1.tpg` | 243,990 B | `863ca2ef1b8efa7bd63b13367fad1ae6c3ef7eb242dcc50468511d543a45d198` | 仅自报绮楼/原作者 ray；未找到可验证公开 Git 源或许可 | 只读交互参考 |
| `Tavo_兽人牧场_1kYBH.json` | 461,410 B | `d9d73276886d70c19deebd4f3c487876c055d32a418e830acde5218b7ef66a99` | 无作者、URL、commit、license 字段 | 只读 schema/pipeline 参考 |

平台规范只采用官方手册：[TavoJS API](https://docs.tavoai.dev/cn/guides/javascript-api/)、[插件开发](https://docs.tavoai.dev/cn/guides/plugin-development/)、[EJS 模板](https://docs.tavoai.dev/cn/guides/ejs-template/)、[世界书](https://docs.tavoai.dev/cn/guides/lore-book/) 与 [正则](https://docs.tavoai.dev/cn/guides/regular/)。第三方包和旧快照都不能覆盖官网合同。

完整机器可读来源登记见 `manifests/intake-sources.json`。

## 3. 完整性与安全接收

### 3.1 Projects 交接包

- 外 ZIP 2,852 entries，0 重名、0 绝对路径、0 `..`、0 symlink。
- 展开 2,381 文件、158,658,164 B。
- 50 个内嵌 ZIP/TPG/NPZ 类容器全部 CRC 通过，未见 zip bomb、危险路径或 symlink。
- 269 个 JSON 全部解析通过。
- `FILE_MANIFEST.json` 的 2,324 条记录复核为 0 缺失、0 哈希/大小不符；唯一未列项是 manifest 自身。
- 未按敏感文件名发现 `.env`、私钥或 token；这不等于运行时秘密流审计。

### 3.2 v117 原包

- 外 ZIP、3 个内嵌 ZIP、2 个 TPG 全部结构/CRC 通过。
- 无路径穿越、绝对路径、反斜杠混淆或 symlink。
- 10 个 JSON 路径实体及 9 本书全部解析通过。
- 147 个模块源没有重复 `@id`；五书 21/21/34/17/54，共 147 条。
- v117 没有独立 PNG/JPG/WebP/GIF/SVG/字体/音视频，因此本体无物理立绘可删；内联 SVG 与 CSS 渐变属于允许保留的代码。

### 3.3 两份参考附件

- 小手机 TPG：20 entries、710,735 B 展开，CRC 全过，0 重名/0 整文件重复；17 HTML + 1 JS + manifest + 1 位图。
- 牧场 JSON：严格解析通过，8 条统一 32 字段，0 整条/正文完全重复，无 URL、图片、SVG 或脚本。

## 4. 精确去重与废弃清理

| 范围 | 精确重复组 | 冗余副本 | 可回收 |
|---|---:|---:|---:|
| `Projects.zip` 展开树 | 32 | 61 | 20,254,991 B |
| v117 叶子文件 | 8 | 8 | 72,859 B |
| 小手机 TPG 完整文件 | 0 | 0 | 0 B |
| 牧场 JSON 完整条目 | 0 | 0 | 0 B |

Projects 的最大重复是源码 ZIP、安装 ZIP、资源 ZIP、五书/TPG/报告在 current/out/交付展开目录之间的多层复制。v117 的重复主要是源文件与嵌套 TPG/模块 ZIP 中的相同成员。所有这些运输容器、展开副本和旧版本均未进入 r001 最新工作树。

不能按“文本相似”直接删的语义冗余：小手机 17 个片段共有 456 种跨文件相同行、1,562 次出现，约 42,600 字符可抽公共层；`moments.html` 与 `twitter.html` 行序列相似度 0.6635。蓝图将它们合并为唯一社交领域服务与渠道适配，而不是机械删行。

机器可读处置账见 `manifests/selection-ledger.json`。

## 5. 当前 Aster 实态

### 已有真实实现证据

- 五书源码 36 模块：核心 19 / 功能 5 / 图鉴 1 / 系统 5 / 皮肤 6。
- 25 panel、16 App、62 参数。
- 已有小手机、Data Manager、主题、资源库/资源账、完整 Mod importer、P1 双轨仪表盘、P2 Holo Veil、语义 UI 注册和可访问性基础。
- 接收阶段在隔离副本重建五书并运行既有门：first-gate 713、importer 7、Mod importer 281、UI contract 11、common asset 840、orbit asset 170，均通过。这只证明 Aster 0.9 自身一致，不代表 v117 迁移完成。

### 未完成能力

- 背包、任务、经济/成长的完整事务语义。
- 项目/存档、资源、宿主数据的 Repository v2 闭环。
- 固定六槽严格 parser/coordinator、单帧 snapshot/frame、唯一 EJS 路由。
- 记忆事件、来源化搜索、大纲候选/CAS、回复与生成生命周期。
- 原子 epoch、全量回滚、late attach/teardown 完整性。

旧迁移账的 149 行只覆盖五本引擎和两个插件，遗漏叙事书 3 条及预设 22 条；新版必须使用 172 行七书口径。

## 6. Tavo API 审计

基础调用面条件通过：manifest v2、SemVer、entry、本地化、sidebar action、generation hooks、文件分页/编码、chat readback、实体 CRUD、Theme 特例与 `utils.ask` 处理均有官方合同对应。

蓝图阻断项：

| 级别 | 问题 | 冻结处理 |
|---|---|---|
| Critical | runtime 从同名世界书取 `code` 后以 `new Function(Aster,tavo,...)` 执行，未知内容可获得插件权限 | 可执行代码固定进 TPG，或逐模块 SHA allowlist；未知/变更模块 fail-closed |
| High | 五个远程字体经 `file.save(URL)` 下载但 manifest 无 `network` | 后续优先把有许可字体纳入唯一素材包；保留网络时必须声明权限和用户提示 |
| High | importer 预检未覆盖角色首条消息、正则条目名、Theme 白名单/ARGB | 每种实体在第一次写前完成官方字段校验，写后 readback |
| High | 当前没有单 EJS 路由、预设消费和叙事正则消费 | B6 实现一个 router + 8 markers；25 源块默认 disabled |
| Medium | fragment 拖动依赖五书成功后接管 | fragment 提供最小 draggable fallback，接管时显式卸载 |
| Medium | `window.top`/共享全局不是官方稳定 API | 收口为可销毁的命名空间桥，不把 top DOM 当平台合同 |
| Medium | message scope 只有字符串、无固定 message id | 消息变量必须使用 `{scope:'message',id}` |
| Low | 仍有弃用 `tavo.utils.export` 分支 | 只保留 `tavo.file.export` |

完整调用清单、路径/行号和 14 条平台合同见 `audit/TAVO-API-AUDIT.md`。

## 7. 参考包的不可直接移植风险

小手机包的风险包括：`window.top`/全局污染、123 处 `innerHTML`、15 个网络请求、第三方图片上传、Bearer key 存储、任意 endpoint、API monkey patch、无 teardown、用户正则 ReDoS、固定 340×604 布局和无 safe-area/clamp。其 manifest 还把 `entry` 指向 `panel.html`，没有引用真正注册 hooks 的 `entry.js`；旧字段 `minTavoVersion` 与旧式权限也不符合当前文档。

允许吸收的只有交互责任：单一 app registry、统一 module host、数据化布局、Pointer Events、状态 selector、联系人/社交/相册/钱包等领域边界。附件代码、状态键、网络 provider、封面和权限声明均不复制。

牧场世界书只吸收：类型/实例分离、信息单次落位、阶段结算、初始化/运行态分离、增量 patch、输出分区。成人领域正文、自然语言伪类型、完整思维链要求和 7 条巨型常驻项都不进入核心。

## 8. 人物素材清理

本轮剔除四份明确人物位图，共 4,606,101 B：

- `aster-player-standing.png`
- `aster-orbit-player-open.webp`
- `aster-player-open-v2-source.png`
- 小手机 `cover.jpg`（实际 PNG）

同时清理运行清单、默认值、测试和 CSS 对这些具体文件的引用。三种人物语义槽仍存在，但默认值为空，基础 UI 用非人物网格/光晕降级层。保留的素材类型：78 个唯一 SVG 图标/遮罩/底纹，抽象壁纸和动效，世界球、地图、家园及非人物社交场景。

## 9. 117 → Aster 冻结蓝图

目标为 86 个可执行模块：

| 书 | 目标 |
|---|---:|
| Aster·核心 | 20 |
| Aster·功能 | 28 |
| Aster·图鉴 | 12 |
| Aster·系统 | 18 |
| Aster·皮肤 | 8 |

固定合同：

- 六槽顺序：`<vi-update> → <de> → <note?> → <vi> → <ext?> → <act>`；`</vi>` 为固定字面。
- 四模式仅 `story / visualNovel / worldDev / codeDev`。
- 只有 `aster.v2.prompt.catalog` 与 `aster.v2.narrative.frame` 两个注入变量；每轮各读一次。
- 25 个叙事源块默认 disabled；预设恰好 1 个 EJS router + 8 个官方宿主 marker。
- Repository/Capability 版本为 `aster.repository/v2` / `aster.capability/v2`。
- 所有 durable 写入必须 CAS、写后读回、content hash、receipt；UI 不直写宿主。

七书账共 172 行：147 引擎 + 3 叙事 + 22 预设。当前 r001 为 167 `blueprint-mapped`、5 `retired-verified`、0 `missing/unmapped/assumed`；Aster `implementedVerified` 仍为 0。完整映射见 `blueprint/v117-to-aster-ledger.json`，架构和现有 36 模块逐项去向见 `blueprint/ASTER-117-MASTER-BLUEPRINT.md`。

## 10. r001 实际改动边界

本轮只做接收、去重、分包、人物素材清理和 B0 蓝图，不继续修功能：

- 从 Aster 0.9 选择 36 个当前模块、两个插件源码、测试与必要 fixture builder。
- 不带 `out/`、旧 release/delta、交付展开副本、历史报告、vendor dependencies、参考二进制或截图。
- `aster.asset.orbit-holo` 从 12 项降为 11 项，移除角色位图。
- 世界媒体只保留地图；家园复用唯一 orbit WebP，删除重复高分辨率母图。
- 玩家/社交人物位改为空语义槽，宠物页不再错误复用玩家立绘。
- 新增来源账、选择账、86 模块机器合同、172 行迁移账和确定性双包构建器。

这些是用户明确要求的边界性清理，不是未经蓝图的功能修补。

## 11. 双包边界

代码包包含：当前源码、插件、测试、构建工具、审计、蓝图、迁移账和来源/处置 manifest；不含运行素材、旧输出或嵌套交付包。

素材包包含：唯一运行图标、SVG、遮罩、底纹、抽象壁纸、动效与允许的非人物场景图；不含代码、人物位图、截图、mockup、旧 ZIP 或制作源副本。

构建器必须同时拒绝：整文件 SHA 重复、跨包相同成员、嵌套 archive、人物位图路径、素材清单漂移、悬空的已删除素材引用、重复模块 ID、非法 JSON/SVG/位图。

## 12. 验证状态

| 门 | 结果 |
|---|---|
| 五书构建 | PASS；19/5/1/5/6，共 36 模块 |
| first gate | PASS；710 checks（人物位图相关断言已改为空槽/无清单断言） |
| importer boundary | PASS；7 checks |
| complete Mod importer | PASS；281 checks；幂等、回滚、增量合并、媒体与源清理均通过 |
| UI contract | PASS；11 checks；276 CSS classes、284 registered、0 missing |
| common asset 深度门 | 接收阶段对当前相同 82 个 runtime 文件执行 840 checks，PASS |
| 浏览器门 | 明确 SKIP；本环境没有 Playwright Chromium executable，不伪报真实浏览器通过 |
| 当前工作树内容唯一性 | PASS；168 个纳入双包的源文件，0 精确重复组，0 人物位图 |
| 双包 | PASS；代码 72 members、素材 98 members；各自 0 重复路径/内容，跨包 0 相同 member 内容 |
| CRC/安全路径/空目录解包 | PASS；两个 ZIP `testzip`、路径穿越/symlink 检查和 clean extraction 文件数一致 |

真实 Tavo 设备安装、宿主拖动 fallback、EJS 路由和 86 模块行为仍属于后续阶段，未在 r001 冒充通过。

## 13. Git 连续性

目标仓库：公开 `Vic-of-yours/-Tavo`，独立分支 `codex/117-to-aster-blueprint`，以 draft PR 交付，不直接覆盖 `main`。

`Projects.zip` 单文件 111,563,600 B，超过 GitHub 普通 Git 单文件 100 MiB 限制；因此远端保存展开后的唯一最新工作树/双包、完整来源哈希和 Git 审计记录，不把大外包再次嵌入仓库。旧版本只留远端提交历史或来源哈希，不出现在最新包。

## 14. 下一步

从 B1 开始构建核心 20：先实现静态/验签模块加载、原子 epoch、lifecycle、registry/services、schema/store、commands/forms、surfaces/host、assets/imports、renderer/diagnostics/workbenches。B1 未通过前不开始迁移 UI 功能，也不创建空壳凑 86。
