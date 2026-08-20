# 117 → Aster 完整蓝图：Aster 0.9.0 与 Vic r189 架构合流审计

> 审计日期：2026-08-20  
> 性质：只读架构审计；不是实现完成声明，也不是发布验收报告。  
> 结论先行：**建议冻结为 86 个可执行模块：核心 20、功能 28、图鉴 12、系统 18、皮肤 8。** 另保留 25 个默认禁用的叙事源分块；预设、TPG 宿主和静态素材包均不计入五书模块数。

本文件现作为 `117-to-aster-blueprint-r001` 的 B0 冻结蓝图。当前可执行源码仍是经定向清理后的 Aster 36 模块，不把规划中的 86 模块冒充已实现。r001 已完成代码包/素材包边界、来源账、精确内容去重门和人物位图清理：三个角色语义槽保留但默认空，基础包只提供非人物的 CSS 降级层；真正人物内容只能由世界 Mod 或用户资源显式注入。

## 1. 审计范围与信任边界

比较对象：

- Aster 当前工作区：`intake/projects_raw/Projects/工作区/01_CURRENT_PROJECT/aster-workspace`
- Vic 完整基线：`sources/r189-baseline`

本次只读取清单、源码文本、蓝图、迁移账、测试定义与已生成报告；**没有执行、导入或 `eval` 任一来源包/参考包，也没有修改两套源码。** 唯一运行的是维护技能自带的可信只读审计脚本，用于核对随技能分发的 r189 基线资产与验收清单。

可复核证据：

| 证据 | SHA-256 / 结果 |
|---|---|
| Aster `out/aster-module-inventory.json` | `26ed01851b61023c7550ce7ec50e11ea3fa9cc4479c8b118ab096f47579ee278` |
| Aster `README.md` | `ccf94f5d131a9f6fa9c9575de22c1304da252674266bfe38eb80d14b4a1d7ba2` |
| r189 `out/Vic-vNext-System-r189-manifest.json` | `6cb8db1884eb847ad3a0ac185de4221a23164dffbc72c69430ba397117845bb3` |
| Aster 当前五书 | 36 模块：19 / 5 / 1 / 5 / 6 |
| r189 五书基线 | 83 模块：19 / 28 / 11 / 17 / 8 |
| 可信基线审计 | 32 资产、25,946,763 字节；83 模块、25 禁用叙事分块、83 题脚手架、21 个测试入口；r117 账 172/172、5 项显式允许退役、0 缺失 |

边界说明：Aster 的“五书 36/36 已写回且一致”只证明当前 36 个条目的本地/宿主内容一致，不等于五书能力完整。Aster 自己的 v117 账目前仍是 **2 条 `migrated_verified`、29 条 `partial`、118 条 `pending`**；不得用“已写回”替代“已迁移”。

## 2. 总裁决：不是 36 + 83，而是 83 骨架吸收 Aster 的唯一能力

直接相加会得到 119 个模块，并把注册表、宿主、主题、资源、导入、手机壳、表单和自检各做两套。这违反“一个职责只能有一个实现”。正确合流方式是：

1. 以 r189 的分层、事务、协议、Repository/Capability 和验收语义作为运行骨架。
2. 把 Aster 已完成且 r189 没有同等产品表达的手机、数据管理、主题、资源、Mod 导入和 Selected UI 能力，落到骨架中的唯一所有者。
3. Aster 现有原型模块能拆则拆、能并则并；只保留行为与唯一数据，不保留重复服务、重复运行入口或旧命名壳。
4. 目标数从 r189 的 83 只净增 3，不制造兼容空壳：

| 增量 | 目标模块 | 原因 |
|---:|---|---|
| +1 核心 | `aster.kernel.workbenches` | 承接 Aster 通用集合工具/工作台注册；只能含纯算法与声明式工作台，不直接写宿主数据。 |
| +1 图鉴 | `aster.repository.host-data` | 承接 Tavo 原生世界书、角色卡、正则、预设的薄适配与读回；Data Manager 不得直连宿主 API。 |
| +1 系统（净增） | 把 r189 的 `repository-apps` 拆成 `project-save-apps` 与 `data-manager` | 项目/存档业务与宿主数据/资源管理是两个产品边界；拆开后仍各只有一个所有者。 |

### 2.1 冻结后的交付计数

| 书 | 当前 Aster | r189 基线 | Aster 目标 | 说明 |
|---|---:|---:|---:|---|
| Aster·核心 | 19 | 19 | **20** | r189 19 + `kernel.workbenches` |
| Aster·功能 | 5 | 28 | **28** | 完整采用 r189 功能分层，不另开 UI/资源逻辑 |
| Aster·图鉴 | 1 | 11 | **12** | r189 11 + `repository.host-data` |
| Aster·系统 | 5 | 17 | **18** | `repository-apps` 拆成两个唯一 UI 所有者 |
| Aster·皮肤 | 6 | 8 | **8** | Aster 视觉并入 r189 八个皮肤域，不保留第二套 CSS 服务 |
| **五书合计** | **36** | **83** | **86** | 可执行模块唯一 ID 数 |

五书之外固定为：

- `Aster·叙事书`：25 个 `disabled` 源分块，只作为可选路由源，不是可执行模块。
- `Tavo_Aster_预设·叙事协议`：恰好 1 个自定义 EJS 路由 + 8 个启用的宿主 marker。
- `io.aster.narrative.runtime`：唯一运行宿主 TPG。
- `io.aster.mod-importer`：唯一完整 `aster.mod/v1` 包导入 TPG。
- 图标、SVG、底纹与其他唯一静态资源：按内容哈希存放在资源包/清单中，不冒充模块。

**86 是施工蓝图，不是当前通过数。** 不允许先创建 50 个空壳把清单凑到 86；模块只有在实现、依赖、行为探针和迁移账同时通过后才计入完成。

### 2.2 当前实态与主要缺口

Aster 0.9.0 当前可审计到 25 个 panel、16 个 App 和 62 个参数，手机/Data Manager/主题/资源/Mod importer/Selected UI 已有真实实现证据；但其中 9 个叙事类 App 仍主要是后续路由骨架。背包、任务、项目/存档、严格协议、记忆、搜索、大纲及多媒体数据闭环尚未达到 r189 同等语义。当前 runtime 也尚无 r189 的原子 epoch/全量回滚。因此本报告把这些列为待施工能力，而不把 UI route、接口登记或 36/36 写回冒充完成。

## 3. 冻结后的 86 模块清单

### 3.1 Aster·核心（20）

1. `aster.kernel.foundation`
2. `aster.kernel.platform`
3. `aster.kernel.lifecycle`
4. `aster.kernel.events`
5. `aster.kernel.registry`
6. `aster.kernel.services`
7. `aster.kernel.schema`
8. `aster.kernel.store`
9. `aster.kernel.commands`
10. `aster.kernel.forms`
11. `aster.kernel.styles`
12. `aster.kernel.surfaces`
13. `aster.kernel.host`
14. `aster.kernel.assets`
15. `aster.kernel.imports`
16. `aster.kernel.import-routes`
17. `aster.kernel.renderer`
18. `aster.kernel.diagnostics`
19. `aster.kernel.selftest`
20. `aster.kernel.workbenches`

### 3.2 Aster·功能（28）

1. `aster.function.contracts`
2. `aster.function.registries`
3. `aster.function.runtime`
4. `aster.function.commands`
5. `aster.function.transactions`
6. `aster.function.effects`
7. `aster.function.context`
8. `aster.function.modes`
9. `aster.function.rules`
10. `aster.function.random`
11. `aster.function.clock`
12. `aster.function.scheduler`
13. `aster.function.inventory`
14. `aster.function.economy`
15. `aster.function.quests`
16. `aster.function.progression`
17. `aster.function.continuity`
18. `aster.function.narrative-queue`
19. `aster.function.generation`
20. `aster.function.snapshot-providers`
21. `aster.function.narrative-frame`
22. `aster.function.frame-publisher`
23. `aster.function.protocol-parser`
24. `aster.function.memory-events`
25. `aster.function.protocol-coordinator`
26. `aster.function.bootstrap`
27. `aster.function.replies`
28. `aster.function.selftest`

### 3.3 Aster·图鉴（12）

1. `aster.repository.contracts`
2. `aster.repository.codec`
3. `aster.repository.catalog`
4. `aster.repository.reducers`
5. `aster.repository.project`
6. `aster.repository.save`
7. `aster.repository.selectors`
8. `aster.repository.resources`
9. `aster.repository.projections`
10. `aster.repository.selftest`
11. `aster.repository.narrative-snapshot`
12. `aster.repository.host-data`

### 3.4 Aster·系统（18）

1. `aster.system.contracts`
2. `aster.system.preferences`
3. `aster.system.prompt-bridge`
4. `aster.system.shell`
5. `aster.system.form-renderer`
6. `aster.system.mode-controls`
7. `aster.system.markers-blocks`
8. `aster.system.message-renderer`
9. `aster.system.capability-adapters`
10. `aster.system.search`
11. `aster.system.outline-workbench`
12. `aster.system.project-save-apps`
13. `aster.system.data-manager`
14. `aster.system.social-media-apps`
15. `aster.system.dashboard-review`
16. `aster.system.selftest`
17. `aster.system.appearance`
18. `aster.system.generation-lifecycle`

### 3.5 Aster·皮肤（8）

1. `aster.skin.tokens-themes`
2. `aster.skin.shell-forms`
3. `aster.skin.protocol-markers`
4. `aster.skin.repository-cards`
5. `aster.skin.top-dashboard`
6. `aster.skin.social-media-vn`
7. `aster.skin.ambient-enhancers`
8. `aster.skin.responsive-accessibility`

## 4. Aster 当前 36 模块的唯一去向

“退役可执行模块”只表示不再作为第二份运行实现；其中唯一的视觉、字段、文案、样例数据和迁移证据必须先抽出到目标模块、静态素材清单或测试夹具，不能直接删除。

| 当前 Aster 模块 | 裁决 | 唯一目标 / 去向 |
|---|---|---|
| `aster.core.lib` | 合并重构 | `aster.kernel.foundation`；通用原语只保留一份。 |
| `aster.core.registries` | 拆分替换 | `aster.kernel.registry` + `aster.kernel.services`；退役“注册表的注册表”。 |
| `aster.core.slots` | 拆分 | `aster.kernel.surfaces` + `aster.kernel.host`；DOM 槽树与宿主绑定分离。 |
| `aster.panel.registry` | 合并 | 声明进 `aster.system.contracts`，打开/路由进 `aster.system.shell`。 |
| `aster.ui.contracts` | 拆分 | 结构语义进 `kernel.surfaces`/`system.contracts`，样式合同进 `kernel.styles`；不得在 Core 携带 CSS 实现。 |
| `aster.app.shell` | 合并 | `aster.system.shell`，成为唯一应用路由与手机壳控制器。 |
| `aster.core.singletons` | 拆分 | 生命周期进 `aster.kernel.lifecycle`，UI 单例投影进 `aster.system.shell`。 |
| `aster.standalone.shell` | 合并 | 宿主无关表面进 `kernel.surfaces`，产品壳进 `system.shell`。 |
| `aster.ui.capabilities` | 拆分 | 服务/生命周期进 `kernel.services`/`kernel.lifecycle`；UI capability 声明进 `system.contracts`。 |
| `aster.ui.composer` | 拆分 | 样式组合合同进 `kernel.styles`；主题/组件投影进 `system.appearance`。 |
| `aster.collection.tools` | 保留能力、重构 ID | 新增 `aster.kernel.workbenches`；只放 filter/search/sort/export/delete 等纯工具和声明式工作台，不直接写宿主。 |
| `aster.form.schema` | 拆分 | `kernel.schema` + `kernel.forms` + `system.form-renderer`；Core 不生成产品 HTML。 |
| `aster.skin.contracts` | 拆分 | `kernel.styles` + `system.preferences` + `skin.tokens-themes`。 |
| `aster.blueprint.contracts` | 最终退役运行态 | 83 个 r188 边界保留为迁移账、fixture 与 conformance；真实模块未通过前不得宣称它们已实现。 |
| `aster.shell.mounter` | 合并 | `aster.kernel.host`；宿主 attach/detach/late-attach 唯一实现。 |
| `aster.shell.overlay` | 拆分 | 表面合同进 `kernel.surfaces`，行为进 `system.shell`。 |
| `aster.shell.panel` | 合并 | `aster.system.shell`。 |
| `aster.panel.developer` | 拆分 | 诊断进 `kernel.diagnostics`；项目/存档入口进 `system.project-save-apps`；验收视图进 `system.selftest`。 |
| `aster.core.selftest` | 拆分 | 核心不变量进 `kernel.selftest`，产品/UI 门禁进 `system.selftest`。 |
| `aster.params.core` | 拆分 | schema/store/commands/forms 进 Core；玩法参数进 `function.rules`；UI 偏好进 `system.preferences`。不得继续作为万能参数模块。 |
| `aster.asset.library` | 拆分 | 文件加载/缓存进 `kernel.assets`；持久资源条目进 `repository.resources`。 |
| `aster.asset.ledger` | 合并重构 | `aster.repository.resources`；固定资源书、重命名、去重、垃圾桶与 tombstone 只有一份。 |
| `aster.asset.common-ui` | 退役可执行态 | 唯一图标/SVG/底纹变成静态资源目录与内容哈希清单，由 `kernel.assets`/`system.appearance` 消费。 |
| `aster.asset.orbit-holo` | 退役可执行态 | 双轨/Holo 唯一资源变成静态清单，由 `dashboard-review`/`social-media-apps`/`appearance` 消费。 |
| `aster.catalog.bootstrap` | 拆解后退役原型 | 数据种子保留为 migration/fixture；真实能力由 12 个 Repository 模块及 System 应用消费，不保留第二套图鉴仓库。 |
| `aster.theme.service` | 合并 | 状态真值进 `system.preferences`，主题解析/投影进 `system.appearance`。 |
| `aster.theme.app` | 合并 | 仍保留独立“主题”App 路由，但实现归 `system.appearance`。 |
| `aster.data.manager` | 保留产品、重构 | `system.data-manager`；数据读写只经 `repository.host-data`/`repository.resources`，通用操作调用 `kernel.workbenches`。 |
| `aster.phone.core` | 保留产品、合并 | `system.shell`；小手机窗口、双标签、底栏、返回/关闭/深链只有一个状态机。 |
| `aster.dashboard.world` | 拆分 | P1 双轨/世界审阅进 `system.dashboard-review`；P2 Holo Veil 进 `system.social-media-apps`。 |
| `aster.skin.preference-registry` | 拆分 | 皮肤默认声明进 `skin.tokens-themes`；运行注册和用户值进 `system.preferences`。 |
| `aster.skin.tokens` | 合并 | `skin.tokens-themes`。 |
| `aster.skin.composed-components` | 拆分 | 壳/表单进 `skin.shell-forms`；数据/资源卡片进 `skin.repository-cards`。 |
| `aster.skin.app-components` | 拆分 | `skin.shell-forms` + `skin.repository-cards`；按渲染对象归属，不再按“App”再建一套组件库。 |
| `aster.skin.shell` | 拆分 | `skin.shell-forms`、`skin.top-dashboard`、`skin.social-media-vn`、`skin.responsive-accessibility`。 |
| `aster.skin.forms` | 合并 | `skin.shell-forms` + `skin.responsive-accessibility`。 |

## 5. r189 的 83 模块映射到 Aster 目标

### 5.1 核心：19 → 19（另新增 1 个 Aster 模块）

| r189 | Aster 目标 |
|---|---|
| `vic.kernel.foundation` | `aster.kernel.foundation` |
| `vic.kernel.platform` | `aster.kernel.platform` |
| `vic.kernel.lifecycle` | `aster.kernel.lifecycle` |
| `vic.kernel.events` | `aster.kernel.events` |
| `vic.kernel.registry` | `aster.kernel.registry` |
| `vic.kernel.services` | `aster.kernel.services` |
| `vic.kernel.schema` | `aster.kernel.schema` |
| `vic.kernel.store` | `aster.kernel.store` |
| `vic.kernel.commands` | `aster.kernel.commands` |
| `vic.kernel.forms` | `aster.kernel.forms` |
| `vic.kernel.styles` | `aster.kernel.styles` |
| `vic.kernel.surfaces` | `aster.kernel.surfaces` |
| `vic.kernel.host` | `aster.kernel.host` |
| `vic.kernel.assets` | `aster.kernel.assets` |
| `vic.kernel.imports` | `aster.kernel.imports` |
| `vic.kernel.import-routes` | `aster.kernel.import-routes` |
| `vic.kernel.renderer` | `aster.kernel.renderer` |
| `vic.kernel.diagnostics` | `aster.kernel.diagnostics` |
| `vic.kernel.selftest` | `aster.kernel.selftest` |

Aster 额外且唯一：`aster.kernel.workbenches`。

### 5.2 功能：28 → 28

| r189 | Aster 目标 |
|---|---|
| `vic.function.contracts` | `aster.function.contracts` |
| `vic.function.registries` | `aster.function.registries` |
| `vic.function.runtime` | `aster.function.runtime` |
| `vic.function.commands` | `aster.function.commands` |
| `vic.function.transactions` | `aster.function.transactions` |
| `vic.function.effects` | `aster.function.effects` |
| `vic.function.context` | `aster.function.context` |
| `vic.function.modes` | `aster.function.modes` |
| `vic.function.rules` | `aster.function.rules` |
| `vic.function.random` | `aster.function.random` |
| `vic.function.clock` | `aster.function.clock` |
| `vic.function.scheduler` | `aster.function.scheduler` |
| `vic.function.inventory` | `aster.function.inventory` |
| `vic.function.economy` | `aster.function.economy` |
| `vic.function.quests` | `aster.function.quests` |
| `vic.function.progression` | `aster.function.progression` |
| `vic.function.continuity` | `aster.function.continuity` |
| `vic.function.narrative-queue` | `aster.function.narrative-queue` |
| `vic.function.generation` | `aster.function.generation` |
| `vic.function.snapshot-providers` | `aster.function.snapshot-providers` |
| `vic.function.narrative-frame` | `aster.function.narrative-frame` |
| `vic.function.frame-publisher` | `aster.function.frame-publisher` |
| `vic.function.protocol-parser` | `aster.function.protocol-parser` |
| `vic.function.memory-events` | `aster.function.memory-events` |
| `vic.function.protocol-coordinator` | `aster.function.protocol-coordinator` |
| `vic.function.bootstrap` | `aster.function.bootstrap` |
| `vic.function.replies` | `aster.function.replies` |
| `vic.function.selftest` | `aster.function.selftest` |

### 5.3 图鉴：11 → 11（另新增 1 个 Aster 模块）

| r189 | Aster 目标 |
|---|---|
| `vic.repository.contracts` | `aster.repository.contracts` |
| `vic.repository.codec` | `aster.repository.codec` |
| `vic.repository.catalog` | `aster.repository.catalog` |
| `vic.repository.reducers` | `aster.repository.reducers` |
| `vic.repository.project` | `aster.repository.project` |
| `vic.repository.save` | `aster.repository.save` |
| `vic.repository.selectors` | `aster.repository.selectors` |
| `vic.repository.resources` | `aster.repository.resources` |
| `vic.repository.projections` | `aster.repository.projections` |
| `vic.repository.selftest` | `aster.repository.selftest` |
| `vic.repository.narrative-snapshot` | `aster.repository.narrative-snapshot` |

Aster 额外且唯一：`aster.repository.host-data`。

### 5.4 系统：17 → 18

| r189 | Aster 目标 |
|---|---|
| `vic.system.contracts` | `aster.system.contracts` |
| `vic.system.preferences` | `aster.system.preferences` |
| `vic.system.prompt-bridge` | `aster.system.prompt-bridge` |
| `vic.system.shell` | `aster.system.shell` |
| `vic.system.form-renderer` | `aster.system.form-renderer` |
| `vic.system.mode-controls` | `aster.system.mode-controls` |
| `vic.system.markers-blocks` | `aster.system.markers-blocks` |
| `vic.system.message-renderer` | `aster.system.message-renderer` |
| `vic.system.capability-adapters` | `aster.system.capability-adapters` |
| `vic.system.search` | `aster.system.search` |
| `vic.system.outline-workbench` | `aster.system.outline-workbench` |
| `vic.system.repository-apps` | **拆为** `aster.system.project-save-apps` + `aster.system.data-manager` |
| `vic.system.social-media-apps` | `aster.system.social-media-apps` |
| `vic.system.dashboard-review` | `aster.system.dashboard-review` |
| `vic.system.selftest` | `aster.system.selftest` |
| `vic.system.appearance` | `aster.system.appearance` |
| `vic.system.generation-lifecycle` | `aster.system.generation-lifecycle` |

### 5.5 皮肤：8 → 8

| r189 | Aster 目标 |
|---|---|
| `vic.skin.tokens-themes` | `aster.skin.tokens-themes` |
| `vic.skin.shell-forms` | `aster.skin.shell-forms` |
| `vic.skin.protocol-markers` | `aster.skin.protocol-markers` |
| `vic.skin.repository-cards` | `aster.skin.repository-cards` |
| `vic.skin.top-dashboard` | `aster.skin.top-dashboard` |
| `vic.skin.social-media-vn` | `aster.skin.social-media-vn` |
| `vic.skin.ambient-enhancers` | `aster.skin.ambient-enhancers` |
| `vic.skin.responsive-accessibility` | `aster.skin.responsive-accessibility` |

## 6. 单一职责冻结表

| 领域 | 唯一真值 / 执行所有者 | 允许的消费者 | 禁止的第二实现 |
|---|---|---|---|
| 模块注册 | `kernel.registry` + `kernel.services` | 全书 | `core.registries` 兼容注册树、System 私有注册表 |
| 运行生命周期 | `kernel.lifecycle` | runtime TPG、各模块 dispose | `singletons`/phone 各自维护启动状态 |
| 宿主根与挂载 | 物理根由 runtime TPG；桥接由 `kernel.host`；表面树由 `kernel.surfaces` | `system.shell` | TPG 与世界书各生成一套手机/面板 DOM |
| 状态写入 | `function.commands → transactions → effects` | Repository/Capability adapters | UI 直改变量、Repository 绕过事务 |
| 项目/存档 | `repository.project` + `repository.save` | `system.project-save-apps` | Data Manager 自建项目/存档格式 |
| 原生宿主数据 | `repository.host-data` | `system.data-manager` | Data Manager 直接调用 Tavo API |
| 资源 | `kernel.assets` 管文件/缓存；`repository.resources` 管持久账/垃圾桶 | Data Manager、Appearance、各 renderer | asset.library、asset.ledger、主题各持一份索引 |
| 完整 Mod 包导入 | `io.aster.mod-importer` | System picker | Data Manager 再放 ZIP/URL/自由文本导入器 |
| 原生对象转换 | `kernel.imports` + `kernel.import-routes` | Repository、Mod importer | 任意页面自行解析角色卡/世界书/正则/预设 |
| 主题 | `system.preferences` 为状态真值；`system.appearance` 为解析与 App 投影；Skin 只画 | Shell、renderer | theme.service/theme.app/Skin 各保存一份值 |
| 四模式 | `function.modes` | `system.mode-controls`、EJS 路由 | UI 或预设自创第五套模式状态 |
| 六槽协议 | `function.protocol-parser` + `protocol-coordinator` | message renderer、Skin | renderer 容错修协议、EJS 改 wire |
| 记忆 | `function.memory-events` 产事件；Repository 持久化/选择 | timeline/review UI、snapshot provider | System 扫聊天重建另一套记忆真值 |
| 搜索 | `system.search` 执行来源调用、provenance、stale | snapshot provider 只消费 ready evidence | Function 发网络请求或把失败伪成空结果 |
| 大纲 | `function.continuity` 为语义真值；`system.outline-workbench` 管候选；Repository 做 durable CAS | generation/frame | 空串覆盖大纲、System 越过 CAS 直写 |
| EJS 注入 | `system.prompt-bridge` 发布 catalog；`generation-lifecycle` 发布 frame；预设只有一个 router | 模型上下文 | 整书注入、多个 router、`aster.snap.*` 散变量 |
| 手机壳 | `system.shell` | Skin、各 App route | runtime TPG/phone.core/standalone.shell 各做壳 |
| P1 Selected UI | `system.dashboard-review` | `skin.top-dashboard` | dashboard.world 单体复刻业务状态 |
| P2 Holo Veil | `system.social-media-apps` | `skin.social-media-vn` | dashboard 世界页另建社交仓库 |

## 7. 不得丢失的叙事与运行协议

### 7.1 五书与加载

- 五本运行书名冻结为 `Aster·核心`、`Aster·功能`、`Aster·图鉴`、`Aster·系统`、`Aster·皮肤`。
- 依赖顺序必须由 manifest/服务图验证，模块 ID 全局唯一；安装失败要原子回滚，不能保留半套 epoch。
- 缺 Repository/Capability 时，assembly/unbound 可报告等待；进入 bound/runtime 后必须 fail-closed，禁止假装 ready。
- 服务合同版本改为 `aster.repository/v2`、`aster.capability/v2`；只换命名空间，不削弱 r189 行为合同。

### 7.2 固定六槽

wire 顺序与可选性冻结为：

`<vi-update>` → `<de>` → 可选 `<note>` → `<vi>` → 可选 `<ext>` → `<act>`

- `</vi>` 必须是固定字面；禁止动态闭合标签。
- `<vi>` 最后一条非空行必须且只能有一次字数终检凭证，然后紧接 `</vi>`。
- 计数口径保持 `visibleCodePointsNoWhitespace/v1`：NFC、去空白、按 Unicode code point 实测；模型自报不能覆盖机器实测。
- parser 严格拒绝错序、重复/未知槽、坏 JSON、未知 op、越权 actor、旧 frame、坏 marker/ext/act；不得“尽量提取”或局部提交。
- durability/readback 成功之前，marker AST、ExtViewRef、ActViewModel、VN scene 均不可交互。

### 7.3 EJS 单帧分块

- 变量只保留 `aster.v2.prompt.catalog` 与 `aster.v2.narrative.frame`。
- 路由每轮各读取一次 catalog 和 frame；不得回退 `vic.snap.*` 或新造 `aster.snap.*`。
- 叙事书的 25 个源 entry 全部默认 `disabled`；EJS 根据 mode、phase、requires 与 selection 选择分块，禁止全文注入。
- 预设必须恰好 9 条：1 个 EJS router + 8 个宿主 marker：`personaDescription`、`scenario`、`worldInfoBefore`、`worldInfoAfter`、`charDescription`、`charPersonality`、`dialogueExamples`、`chatHistory`。
- 83 题显式脚手架、`reasoning_effort=high`、`show_thoughts=false` 保持；`<de>` 是公开核验回执，不是要求披露私有推理过程。

### 7.4 四模式

唯一模式集合为：

| ID | 必须保留的差异 |
|---|---|
| `story` | 连续叙事、真实停点、玩家代理权、公开动作 A–H |
| `visualNovel` | 同六槽协议，加 VN scene/角色呈现投影，不另造协议 |
| `worldDev` | 世界开发与生成调度问题，仍走同一 frame/wire |
| `codeDev` | 代码开发与生成调度问题，仍走同一 frame/wire |

模式切换真值只在 `function.modes`；按钮在 `system.mode-controls`；EJS 只读当前 frame 的 `modeId`。

## 8. Repository、Capability、记忆、搜索、大纲的闭环

### 8.1 Repository

- 项目书：`Aster·图鉴·{项目}`。
- 存档书：`Aster·存档·{项目}·{存档名}`。
- 固定资源书：`Aster·资源书`。
- 所有 durable 写入必须带 expected revision/CAS、写后读回、content hash 与 receipt；不能只把“API 调用成功”当成持久化成功。
- `repository.host-data` 只做原生对象适配和读回，不吞并项目/存档/资源领域。

### 8.2 Capability

- 网络搜索、文本生成、资源镜像、媒体等外部动作只经 `aster.capability/v2` adapter。
- probe 必须报告 available/revision/capacity；timeout、abort、retry 与 stale 明示。
- credential/header/secret 不得进入 frame、日志、资源账或诊断输出。

### 8.3 记忆、搜索和大纲

- MemoryEvent 保留确定性事件、因果/得失/场面锚/信息分层/余波/时间/粒度/伏笔/视角/核销语义；不是摘要文本堆。
- 搜索条目必须携带来源、claim/evidence 关系、fresh/stale 状态和失败诊断；不能把无来源文本放进 frame。
- 大纲空串不改；非空候选整份替换；accept/reject/orphan 明示，接受时校验 candidate hash 与 expected revision。
- snapshot provider 只选择已经 ready 且 revision 对齐的项目、存档、记忆、搜索、大纲和资源投影，发布单一 immutable frame。

## 9. TPG 宿主与 Mod 导入的合流决定

### 9.1 `io.aster.narrative.runtime`

Aster 当前 0.9.0 runtime 是顺序分发，并使用动态函数执行模块；其 HTML shell 还直接创建手机/仪表盘按钮。目标要保留 Aster 插件 ID、权限、本地化和宿主兼容，但替换为 r189 已验证的运行模型：

- TPG 只提供三个最小宿主片段/根、manifest 加载、原子 epoch、late attach 与卸载。
- 业务 UI、按钮、App 路由移交 `system.shell`；视觉移交 Skin。
- 任一模块失败即整轮回滚；不得留下部分服务、重复 listener 或孤立 DOM。
- 无宿主启动后，fragment 晚到仍能挂载；重复 attach 幂等。

### 9.2 `io.aster.mod-importer`

- 继续作为五书之外的独立插件，不计入 86。
- 它是唯一完整 `aster.mod/v1` ZIP/package 导入入口，保留事务回滚、幂等、同名更新、增量世界书合并、内嵌媒体与源清理。
- Data Manager 只管理已存在的 Data/Resources；不得恢复 URL/自由文本包导入或第二套 ZIP parser。
- `kernel.imports`/`import-routes` 仅承接受控的原生对象预览、转换和 copy-source draft；包编排仍归 Mod importer。

## 10. Aster 产品能力的保留证明

| Aster 能力 | 目标落点 | 保留条件 |
|---|---|---|
| 小手机 | `system.shell` + `skin.shell-forms`/`responsive-accessibility` | 小窗、双标签、底栏、深链、返回/关闭、窄屏和 late attach 均过行为测试。 |
| Data Manager | `system.data-manager` | 只保留 Data/Resources 两标签；五类宿主对象经 `repository.host-data`，资源经 `repository.resources`。 |
| 主题 | `system.preferences` + `system.appearance` + `skin.tokens-themes` | 独立主题 App 保留；状态、解析、绘制三层不互相持久化。 |
| 资源库/资源账 | `kernel.assets` + `repository.resources` | 唯一哈希、重命名、去重、垃圾桶、readback、引用追踪全部保留。 |
| 图标/SVG/底纹 | 静态资源包 + manifest | 不当 JS 模块；保留唯一资源与 provenance，引用缺失必须报错。 |
| Mod 导入 | `io.aster.mod-importer` | 唯一包入口；不能并入 Data Manager 形成双实现。 |
| P1 双轨/世界仪表盘 | `system.dashboard-review` + `skin.top-dashboard` | Selected UI 的双轨、世界球、地点牵引板、同根详情和 7-slot HUD 均保留。 |
| P2 Holo Veil | `system.social-media-apps` + `skin.social-media-vn` | 社交数据来自 Repository/Function；图层只投影，不自建记录。 |
| 旧版终端语义 | `system.shell` + Skin | 黑/青/紫切角、小手机、双标签、首九 App、底栏、七路星标可点击，不以截图冒充行为。 |

素材清理已在 r001 执行：经尺寸、透明度、引用关系与人工复核确认的四份人物位图没有进入最新工作树，相关默认值改为空槽；图标、SVG、底纹及非人物 Selected UI 运行资源继续保留。后续模块退役仍不得误删其唯一素材。

## 11. v117 迁移账的统一口径

当前 Aster 的 149 行账只覆盖五本引擎条目与两个插件，且完成度为 2/149；它不能作为最终关账台账。完整蓝图必须采用 r189 已建立的七书源账：

| 来源 | 行数 |
|---|---:|
| 五本引擎书 | 147 |
| 叙事书 | 3 |
| 预设 prompts | 22 |
| **合计** | **172** |

两个插件另设安装与行为验收轨，不并入七书 172 行，避免把“文件存在”与“源条目迁移”混成一个计数：runtime 验证原子装载/late attach/卸载，Mod importer 验证 `aster.mod/v1` 的事务、幂等、合并、媒体与清理。

r189 账当前状态分布：

| 状态 | 数量 | Aster 关账解释 |
|---|---:|---|
| `translated` | 141 | 必须落到一个或多个真实 Aster 模块并有行为证据 |
| `superseded-contract` | 24 | 旧字面由明确的新合同替代，能力语义不得消失 |
| `translated-safe-adapter` | 1 | 只迁移安全适配行为 |
| `superseded-policy` | 1 | 旧策略由新策略明确取代 |
| `retired-inert` | 1 | r117 原内容为空，无运行行为 |
| `retired-explicit` | 4 | 越权/破限提示显式退役，不得恢复 |
| **总计** | **172** | 禁止 `missing`、`unmapped`、`assumed` |

迁移铁律：

1. 172 个源 ID 必须唯一；每项有 source hash、目标模块/策略、状态和测试证据。
2. 一项拆给多个目标时，所有目标都通过才可关闭；某一个 UI 可点击不代表底层能力完成。
3. `partial` 永远不计完成；“合同已登记”“路由占位”“蓝图已写”也不计完成。
4. 只允许上述 5 项退役；其他旧模块可退役的是接口/实现，不是用户可见能力与数据语义。
5. Aster 命名空间替换后应重新生成 172 行账，但保留原 source ID/hash，确保 Git 历史可追溯。

## 12. 建议施工顺序与阶段门

这不是“先造 UI 再补逻辑”的顺序；每一闸只合入已完成、可回滚、可复核的唯一实现。

1. **B0 冻结账本与命名**：锁定 86 清单、172 行源账、服务版本、书名、插件 ID、wire 和变量名；检查零重复 ID/零孤儿目标。
2. **B1 核心 20**：先完成 loader/lifecycle/registry/services/schema/store/commands/forms/surfaces/host/assets/imports/renderer/diagnostics/workbenches；原子失败探针必须过。
3. **B2 功能 28**：完成事务/effects、四模式、玩法域、记忆、单帧 frame、严格 parser/coordinator；固定六槽 golden 全过。
4. **B3 图鉴 12**：完成 `aster.repository/v2`、项目/存档/资源/投影/narrative snapshot/host-data，所有写入有 CAS + readback。
5. **B4 系统 18**：绑定 `aster.capability/v2`，恢复搜索/大纲/项目存档/Data Manager/手机/Selected UI/主题/社交/VN；UI 不直写。
6. **B5 皮肤 8**：接回 Aster 唯一图标/SVG/底纹与 Selected UI 视觉；无业务状态、无隐藏写入；窄屏/减弱动画/键盘可达性过关。
7. **B6 叙事与宿主**：25 disabled chunks、唯一 EJS router、8 markers、runtime late attach、Mod importer 单入口一起验收。
8. **B7 关账与打包**：172/172、86/86、书内/跨书无重复模块或职责；静态资源按内容哈希唯一；立绘清理后零悬空引用；Git 中保留旧历史，最新包只含唯一现行文件。

每阶段的硬失败条件：

- 重复模块 ID、重复 service/provider、重复 DOM host、重复 import route。
- 缺依赖却返回 ready；失败后仍残留 listener/style/root/service。
- 任何 UI 直接写宿主变量或绕过 command/transaction/repository。
- EJS 多于一个、叙事源 entry 被启用、出现整书注入或散变量快照。
- 协议错序被容错、局部提交、读回前开放交互。
- 172 行出现 `missing`/`unmapped`/`assumed`，或把 `partial` 算完成。

## 13. 最终判断

Aster 0.9.0 的价值在于已经形成可操作的手机、数据管理、主题、资源、Mod importer 与 Selected UI；r189 的价值在于完整的五书运行骨架、六槽/EJS/四模式、Repository/Capability、记忆/搜索/大纲与可验证宿主闭环。两者应按本报告合成 **86 个唯一职责模块**，而不是保留两套框架。

下一步可以直接从 B0/B1 开始：先把清单、依赖图、172 行台账和原子 loader 固定，再逐模块迁移。当前不能宣称 86 模块或 172 项已经在 Aster 实现；本报告只给出了可执行、可验收、无重复职责的冻结蓝图。
