# Aster 0.9 Tavo API 合规审计（只读）

审计日期：2026-08-20  
审计对象：`Projects/工作区/01_CURRENT_PROJECT/aster-workspace`  
审计性质：117→Aster 蓝图前置审计；未修改任何项目文件  
规范来源：仅使用 Tavo 官方文档

## 1. 结论

当前 Aster 0.9 的基础 TavoJS 调用名称、异步方式、插件 v2 manifest、侧边栏 action、插件 hooks、文件分页、聊天绑定、实体 CRUD 与 `utils.ask` 返回值处理，大部分与当前官方文档一致。两个最新 TPG 也与对应源码成员逐字节一致。

但它尚不适合作为 117→Aster 的直接施工终点。蓝图期至少需要关闭以下阻断项：

| 级别 | 编号 | 结论 |
|---|---|---|
| Critical | API-C01 | Runtime 从可变世界书读取任意 `code`，再用 `new Function` 以插件注入的 `tavo` 权限执行；只有书名和模块 id 前缀校验，没有内容哈希/签名/静态允许清单。世界书“数据”由此跨越成插件权限代码。 |
| High | API-H01 | Runtime 会经 `tavo.file.save` 下载五个远程字体 URL，但 manifest 未声明 `network`；权限说明与实际能力不一致。 |
| High | API-H02 | Mod 导入器宣称“写入前完整校验”，但预检没有验证角色必需的 `firstMes`/`first_mes`、正则条目必需的名称，也没有按 ChatTheme 白名单/8 位 ARGB 校验主题；错误可能在已经开始事务写入后才由 Tavo 抛出。 |
| High | API-H03 | 当前五书、runtime 和 importer 中没有任何 EJS 路由、预设 API 消费或 runtime 正则 API 消费。不存在违规 EJS，但 117→Aster 的单 EJS 叙事路由/预设链尚未落地。 |
| Medium | API-M01 | `/chat` fragment 的悬浮按钮拖动能力依赖五书成功启动后再绑定；fragment 自身不具备拖动兜底。若模块部分失败后 Skin 仍注入 fixed CSS，按钮可能固定但不可拖。 |
| Medium | API-M02 | Runtime 与 fragment 把 UI 和状态挂到 `window.top`、`window.top.document`、`W.Aster`、`W.__asterShell`。官方只承诺插件上下文中的未限定 `tavo`，未承诺 top-window DOM/共享全局是稳定宿主合同。 |
| Medium | API-M03 | 部分用户可见错误和 Toast 没有进入 catalog；导入器把大量英文异常消息插入已本地化的 `runtime.failed`，shell 也有中文硬编码 Toast。 |
| Medium | API-M04 | 参数层允许字符串 `'message'` scope，却不能传 `{ scope: 'message', id }`。插件 entry/`/chat` 不是消息气泡上下文，按官方语义会落到最后一层，不能稳定绑定指定消息。 |
| Low | API-L01 | 资源导出仍保留已弃用的 `tavo.utils.export` 兼容分支。 |
| Low | API-L02 | fragment 内部版本为 `0.8.0`，runtime manifest/entry 为 `0.9.0`，形成可观察版本漂移。 |

因此本审计给出的状态是：**基础 API 面条件通过；安全边界、导入预检和叙事路由不通过蓝图验收。**

## 2. 唯一规范来源

- [TavoJS API](https://docs.tavoai.dev/cn/guides/javascript-api/)
- [插件开发](https://docs.tavoai.dev/cn/guides/plugin-development/)
- [EJS 模板](https://docs.tavoai.dev/cn/guides/ejs-template/)
- [世界书](https://docs.tavoai.dev/cn/guides/lore-book/)
- [正则](https://docs.tavoai.dev/cn/guides/regular/)

本报告没有把旧插件、第三方实现、现有测试桩或历史文档当作 API 规范。源码测试只可作为实现证据，不能覆盖官方合同。

## 3. 审计边界与方法

审计了以下规范性源码：

- `plugin-runtime/manifest.json`
- `plugin-runtime/entry.js`
- `plugin-runtime/ui/shell.html`
- `plugin-runtime/locales/{en,zh-CN}.json`
- `plugin-mod-importer/manifest.json`
- `plugin-mod-importer/entry.js`
- `plugin-mod-importer/locales/{en,zh-CN}.json`
- `src-modules/**/*.txt`
- 最新 `out/aster-runtime-0.9.0.tpg`
- 最新 `out/aster-mod-importer-1.4.0.tpg`

生成的五书 JSON 是 `src-modules` 的镜像构建物，未作为第二份独立源码重复计数。静态扫描得到 175 个 `tavo.*` token；实体 CRUD 还通过 `apiFor(type)` 间接调用，因此不能只用直接 token 数代表真实调用次数。

## 4. 明确合规项

### 4.1 Manifest 与 TPG

| 项 | Runtime | Mod importer | 判定 |
|---|---|---|---|
| `specVersion` | `2` | `2` | 合规 |
| 插件 id | `io.aster.narrative.runtime` | `io.aster.mod-importer` | 小写、合法字符 |
| 版本 | `0.9.0` | `1.4.0` | 合法 SemVer |
| `entry` | `entry.js` | `entry.js` | 根内相对路径 |
| `minAppVersion` | `0.93.0` | `1.0.0` | 合法 SemVer；importer 对齐 `utils.ask` 的 v1.0.0 起始版本 |
| 本地化 | `en` + `zh-CN` | `en` + `zh-CN` | v2 catalog 合规 |
| Sidebar 声明/handler | 2/2 | 2/2 | id 精确匹配 |
| HTML fragment | `/chat/body/end` | 无 | 合法挂载点、合法本地路径 |
| Settings schema | `info` + `switch` | `info` + 3 `switch` | 合规 |

证据：

- `plugin-runtime/manifest.json:2-30`
- `plugin-mod-importer/manifest.json:2-29`
- `plugin-runtime/entry.js:210-214`
- `plugin-mod-importer/entry.js:1764-1765`
- `plugin-runtime/manifest.json:23-25`

两个最新 TPG 的成员均与当前源码 SHA-256 一致：runtime 的 manifest、entry、两个 locale、`ui/shell.html`；importer 的 manifest、entry、两个 locale。包内成员分别为 5 个和 4 个，无绝对路径、反斜杠或 `../` 成员。

### 4.2 插件上下文与生命周期

- 所有插件 API 均使用未限定的 `tavo`，没有 `window.tavo` 或 `globalThis.tavo`：合规。
- `generation:*` hooks 只在安装插件的 `entry.js` 注册，没有在 HTML fragment 注册：合规。
- Runtime manifest 声明了 `generate` 和 `input`，与相应 hooks 对齐。
- `chat:opened/closed/updated`、`message:added/updated/deleted`、四个 `generation:*`、两个 `input:*` 名称均为官方事件名。

证据：`plugin-runtime/entry.js:198-215`。

### 4.3 文件 API

- `file.list` 使用 `{scope, limit: 200, cursor}` 并遍历 `nextCursor`，符合 1–200 的页大小合同：`src-modules/func/515-resource-library.txt:165-178`。
- `file.import` 传 `extensions: ['zip']`（无点号）、`multiple: false`、`conflict: 'rename'`，并按“总是返回数组、取消返回空数组”处理：`plugin-mod-importer/entry.js:1693-1707`。
- 二进制保存/读取显式使用 `base64`，文本凭证显式使用 `utf8`：`plugin-mod-importer/entry.js:1019-1028, 1108-1118, 1631-1636`。
- 完整虚拟路径与裸文件名两种调用大体分开处理：`src-modules/func/515-resource-library.txt:202-215`、`src-modules/func/516-resource-ledger.txt:454-475`。
- `file.url` 按同步 API 使用；外围 `Promise.resolve` 不改变语义：`src-modules/func/515-resource-library.txt:253-260`。
- 新路径 `file.export` 被优先使用：`src-modules/func/515-resource-library.txt:307-320`、`src-modules/system/730-data-manager.txt:160-163`。

### 4.4 变量、聊天与实体 CRUD

- `tavo.get/set/update/unset` 均按同步 API 使用：`src-modules/core/01-core-lib.txt:103-112`。
- `chat.current()`、`chat.update(patch)` 均 `await`，并执行写后读回：`plugin-mod-importer/entry.js:1286-1321, 1389-1438`。
- Runtime 先用 `lorebook.all()` 取概要，再用 `lorebook.get(id)` 取完整 entries，未把概要中的数字 `entries` 当数组：`plugin-runtime/entry.js:118-133`。
- 资源书同样遵守 `all → get → update/create → get`：`src-modules/func/515-resource-library.txt:385-404, 433-452`；`src-modules/func/516-resource-ledger.txt:258-310`。
- Importer 通过 `find(name,{match:'exact'}) → get(id)` 获取完整实体；普通实体使用对象式 `update(payload)`，ChatTheme 使用官方的 `update(id, patch)` 特例：`plugin-mod-importer/entry.js:780-795, 1033-1081, 1123-1143`。
- `theme.export(id)` 的返回路径接入 `theme.import(path)`/`file.delete(path)`，符合官方虚拟路径模型：`plugin-mod-importer/entry.js:1146-1170`。
- `utils.ask` 使用 object 参数、严格选项和 `status/answer` 返回结构：`plugin-mod-importer/entry.js:913-935`。
- `app.versionNumber()` 被异步读取，`930` 与 `0.93.0` 的数字形式一致：`plugin-runtime/entry.js:218-225`。

### 4.5 HTML fragment 的已实现部分

悬浮入口在五书成功加载后会获得：

- Pointer Events（覆盖鼠标、触摸与支持 Pointer Events 的触控笔）；
- 6px 点击/拖动阈值与 click suppression；
- 全局位置持久化；
- resize 后重新 clamp；
- 可发现的“重置悬浮入口位置”按钮。

证据：

- `src-modules/core/08-capabilities.txt:137-205, 255-267`
- `src-modules/core/60-shell-mounter.txt:17-40`
- `src-modules/func/500-params-core.txt:178-184`
- `plugin-runtime/ui/shell.html:38-63`

这解释了为什么它不是“完全未实现拖动”，但仍有 API-M01 所述的启动前/部分失败窗口。

## 5. 详细问题

### API-C01：可变世界书代码获得插件权限

Runtime 按五个精确书名读取所有启用条目，解析其中的 `code`，随后执行：

```js
new Function('Aster', 'tavo', 'log', 'DOC', ...)
```

证据：

- 书名选择与条目读取：`plugin-runtime/entry.js:5-7, 118-133`
- 仅校验模块 id 前缀：`plugin-runtime/entry.js:40-64`
- 动态编译并传入插件 `tavo`：`plugin-runtime/entry.js:101-110`

风险不是 `new Function` 本身的语法，而是信任边界：任何能够写入同名世界书启用条目的人都可能把数据升级为具有 runtime 插件权限的代码；manifest 的 file/message/generate/input/variable 能力也随之可用。官方把世界书定义为提示词数据，把插件 `entry` 定义为已安装代码；当前设计把两者合并，却没有完整性校验。

蓝图必须二选一并固定：

1. 可执行代码全部静态放入签名/固定 TPG，世界书只保留数据；或
2. 用构建期生成的 `{book,moduleId,version,sha256}` 允许清单逐模块验签，任何未知/变更模块 fail-closed，且绝不能仅凭书名与 `aster.*` 前缀执行。

### API-H01：远程下载与 manifest 权限不一致

Runtime manifest 权限为 `variable/message/generate/input/file`：`plugin-runtime/manifest.json:17`。但 Skin 注册了五个远程字体 URL：

- `src-modules/skin/12-preference-registry.txt:40-44`

资源层会把 URL 直接交给 `tavo.file.save` 下载：

- `src-modules/func/515-resource-library.txt:292-297, 324-348`

官方 manifest 将 `network` 列为应说明的能力；官方文件 API 也明确 `file.save` 的 `http(s)` 内容会下载。当前 manifest 因而低报能力。对于本项目“代码包/素材包分离且素材本地化”的铁律，推荐蓝图直接把字体放入唯一素材包并移除运行时网络下载；若仍保留远程源，则必须声明 `network` 并在 UI 中解释网络行为。

### API-H02：Importer 的“完整预检”未覆盖官方必填字段

Importer 的 `assertEntity` 只统一检查实体 `name`，再检查 entries 的容器类型：`plugin-mod-importer/entry.js:571-588`。这不足以满足官方写 API：

- 角色 `create/update` 需要 `name` 与 `firstMes`（兼容输入可使用 `first_mes`）；当前没有验证首次消息。
- 正则条目 `name` 是必填，否则解析可能失败；当前只验证 `entries` 是数组。
- ChatTheme 使用严格嵌套白名单，颜色必须是 8 位 `#AARRGGBB`；当前 portable theme 只验证 theme 名和包结构：`plugin-mod-importer/entry.js:709-724`。

因此包可以通过 `preparePackage()`，随后在 `executePlan()` 已进入逐项写入阶段才失败。虽然 journal 会尝试回滚，但这不等于“首次写入前完整校验”。蓝图应为每一种 entity 建立与官方字段合同对应的结构校验器，并为 Tavo 可能规范化的字段设置明确 readback 比较集。

### API-H03：EJS/预设/正则叙事运行时缺失

静态检查结果：

- `src-modules`、runtime、importer 中 EJS 标签命中 0；
- 五个最新构建书中 EJS 标签命中 0；
- runtime 源中 `tavo.preset.*` 命中 0；
- runtime 源中 `tavo.regex.*` 命中 0；
- 仅 importer 能作为通用数据导入器写 preset/regex。

所以当前代码并未违反 EJS 子集，但也没有实现 117→Aster 所需的动态提示路由。蓝图必须锁定：EJS 只放在官方支持的提示词字段；使用内置 `getvar`，不假设 EJS 中存在 `tavo.*`；先 EJS 后宏；不使用 `include`/`partial`/自定义分隔符；任何模板错误会导致整字段原样回退，必须有故障测试。

### API-M01：fragment 拖动依赖五书后挂载

`ui/shell.html` 本身只创建按钮、click handler、重置与 i18n handler：`plugin-runtime/ui/shell.html:20-81`。拖动事件直到 `aster.ui.capabilities` 和 `aster.shell.mounter` 模块执行后才绑定。官方要求 `/chat` 中 fixed/absolute 悬浮按钮必须可拖、抑制误点、持久化并限制在视口，且不能遮挡宿主关键控件。

蓝图应让 fragment 自带最小、无五书依赖的 draggable fallback；书内 capability 成功接管时显式卸载 fallback。还需监听 orientation/safe-area 变化，并在失败态保持可拖/可重置。

### API-M02：未文档化的 top-window/共享全局依赖

证据：

- `plugin-runtime/entry.js:8-10, 113-116`
- `plugin-runtime/ui/shell.html:5-9, 35, 66-81`
- `src-modules/core/60-shell-mounter.txt:10-18, 44-50`

官方明确承诺的是 entry、`/chat`、`/messages` 中的未限定 `tavo`，并明确反对 `window.tavo/globalThis.tavo`。当前代码没有触犯后半句，但官方也没有承诺 `window.top.document` 可写或 top 全局永远同源。蓝图应以 fragment 自身 DOM 为宿主，将跨模块通信收口到一个可销毁、命名空间化的桥；不能把 top document 与全局属性视为 Tavo API。

### API-M03：国际化没有覆盖全部用户可见错误

已通过项：四个 catalog 都是扁平 UTF-8 string object；runtime 的 12 个引用键在 en/zh-CN 均存在，importer 静态引用键也无缺失；fragment 会在语言切换时更新两个 `aria-label`。

未通过项：

- 硬编码 Toast：`plugin-runtime/ui/shell.html:46`。
- Runtime 动态模块错误以英文内部消息进入本地化失败 Toast：`plugin-runtime/entry.js:47-79, 149-169`。
- Importer 的大量英文 `fail()/Error` 最终作为 `{message}` 注入 `runtime.failed`：例如 `plugin-mod-importer/entry.js:650-679, 1741-1746`。
- `i18n.onChange` 返回的 unsubscribe 未保存：`plugin-runtime/ui/shell.html:59-64`。

官方完成标准明确包含错误、确认提示和 Toast。蓝图应为错误使用稳定 code，再在展示边界用 catalog 映射；fragment 首次完整 render、语言变化完整 rerender，并在卸载时 unsubscribe。

### API-M04：消息变量没有稳定 message id

参数注册允许 `'message'`：`src-modules/func/500-params-core.txt:11-17, 55-77`，但底层 store 只把 scope 字符串透传：`src-modules/core/01-core-lib.txt:103-112`。

官方规定字符串 `'message'` 在非气泡环境按最后一层处理；只有 `{scope:'message', id:n}` 才稳定指向指定楼层。Aster 运行在插件 entry/`/chat` 层，因此字符串 message scope 不适合作为持久消息投影。蓝图应把 message id 作为必需参数，并禁止业务层隐式“最后一层”。

### API-L01：弃用 API 仍在路径中

`src-modules/func/515-resource-library.txt:307-320` 优先用 `tavo.file.export`，但仍回退到官方已弃用的 `tavo.utils.export`。这不是当前立即故障，但与“最新包无旧兼容冗余”的目标冲突。蓝图应只保留 `file.export`，二进制明确指定 encoding。

### API-L02：Runtime 版本漂移

- Manifest/entry：`0.9.0`，见 `plugin-runtime/manifest.json:5`、`plugin-runtime/entry.js:3`。
- Fragment bridge：`0.8.0`，见 `plugin-runtime/ui/shell.html:66-68`。

版本必须由单一构建元数据生成，并在 TPG 验收中检查 manifest、entry、bridge 一致。

## 6. 调用清单与可验证位置

| API 面 | 调用 | 主要源码证据 | 判定 |
|---|---|---|---|
| App | `app.versionNumber` | `plugin-runtime/entry.js:218-223` | 合规 |
| 变量 | `get/set/update/unset` | `plugin-runtime/entry.js:28-29`; `ui/shell.html:57,79`; `core/01-core-lib.txt:103-112`; importer `1173-1189,1631-1636` | 基本合规；message id 缺口见 M04 |
| Chat | `chat.current/update` | importer `300-305,851-855,1232-1235,1286-1321,1389-1438` | 合规并有读回 |
| Worldbook | `lorebook.all/get/find/create/update/delete` | runtime `118-133`; resource library `385-452`; ledger `258-310`; importer `300-325,780-835,1211-1275,1534-1569` | 调用签名合规 |
| Character | `find/get/create/update/delete`（经 `apiFor`） | importer `780-835,1033-1081,1334-1511` | 签名合规；预检缺必填字段 |
| Preset | 同上（经 `apiFor`） | 同上 | 签名合规；runtime 未消费 |
| Regex | 同上（经 `apiFor`） | 同上 | 签名合规；条目预检不足、runtime 未消费 |
| Theme | `all/find/get/create/update/import/export/delete` | importer `780-835,1033-1170,1334-1511` | update 特例正确；schema 预检不足 |
| File | `list/import/save/load/delete/exists/url/export` | resource library `32-51,125-320`; ledger `320-328,454-475,599-605`; data manager `160-163`; importer `839-848,967-1028,1084-1170,1631-1756` | 基本合规；网络声明与旧 export 分支除外 |
| Utils | `toast/ask/export` | runtime `20`; shell `19`; importer `33-40,913-935`; resource library `307-320` | ask 合规；export 已弃用 |
| Plugin config/i18n | `config.get`, `i18n.t/onChange` | runtime `14-25`; shell `16-19,59-64`; importer `33-40,906-910` | API 合规；可见文案覆盖不足 |
| Plugin hooks | `plugin.on`, `onSidebarAction` | runtime `197-215`; importer `1764-1765` | 注册位置、事件名合规 |

项目中没有直接 `tavo.message.*` 调用，也没有直接 `fetch`、`XMLHttpRequest`、`WebSocket` 或 `EventSource`；远程下载通过 `tavo.file.save(http-url)` 发生。

## 7. 117→Aster 蓝图必须锁定的 Tavo 合同

1. **执行信任边界**：世界书、预设、正则、Mod 都是数据；不得凭书名执行其任意 JS。可执行代码固定在 TPG，或逐模块强制 SHA-256 允许清单。
2. **插件形态**：只用 manifest v2、合法 SemVer、根 `manifest.json`、包内相对 `/` 路径；最新构建中只能存在一个 runtime TPG 与一个 importer TPG。
3. **API 入口**：插件只使用未限定 `tavo`；禁止 `window.tavo/globalThis.tavo`；top-window 与宿主 DOM 不作为持久合同。
4. **权限最小且真实**：manifest 权限必须由静态调用/资源行为生成并验收。若所有素材本地化，移除 network；若任何 URL 下载保留，声明 network。
5. **版本下界**：`minAppVersion` 等于所用最新 API 的最高最低版本；源码、manifest、fragment、构建包版本由同一元数据生成。
6. **变量**：业务默认 chat；跨聊天才用 global；消息投影必须显式 `{scope:'message',id}`；session 只能是内存层，不能伪装成 Tavo scope。
7. **文件**：只允许 chat/global；`list` 完整分页；二进制/文本显式 encoding；完整虚拟路径不再附 scope；新代码只用 `file.export`；网络资源与本地素材不可双份共存。
8. **实体预检**：在第一次写之前按官方合同验证 character、lorebook、preset、regex、theme 全字段；尤其角色首条消息、正则条目名、ChatTheme 白名单与 8 位 ARGB。
9. **写入语义**：`find exact → get full → plan → user confirm → write → get/readback`；`theme.update(id,patch)` 与其它实体 `update(object)` 分开；取消必须是正常结果而不是半成功。
10. **EJS**：一个预设路由入口；只用 Tavo EJS 子集；先 EJS 后宏；无 include/partial；固定读取需要的变量一次；模板错误原样回退必须有测试。
11. **Hooks**：四个 generation hooks 只能在 entry 注册；prepare/success 每个 handler 总预算小于 5 秒；只能改官方可写字段，不把长事务放入 hook。
12. **HTML fragment**：fragment 自身即使五书未加载也能拖动、抑制误点、持久化、clamp、安全区避让与重置；成功接管时卸载兜底监听。
13. **国际化**：所有可见文本、错误、确认、Toast、aria/placeholder 进入 catalog；首次完整渲染、语言变更完整重渲染、卸载 unsubscribe。
14. **可验证交付**：每次构建检查 TPG 成员安全、源码/TPG 哈希一致、权限/调用面一致、无 deprecated API、无未知 EJS、无未签名可执行模块。

## 8. 蓝图验收门

在开始功能迁移前，至少应新增以下静态/动态门：

- `manifest-contract`: v2、路径、SemVer、版本一致、权限与调用/URL 行为一致。
- `tpg-source-parity`: TPG 每个成员与 canonical source SHA-256 一致。
- `module-integrity`: 未在构建 manifest 中的模块或 hash 变化必须拒绝执行。
- `entity-preflight`: 给每类实体投喂缺必填字段/非法主题色/非法正则条目，确认零写入。
- `file-contract`: 分页、取消返回空数组、full-path/no-scope、chat/global 隔离、encoding 回读。
- `message-scope`: 消息追加后仍按固定 message id 读回，不随“最后一层”漂移。
- `hook-budget`: prepare/success 超时与无效修改按官方语义处理，Aster 自身不依赖超时 handler 完成事务。
- `fragment-hostless`: 五书缺失、扫描失败、部分模块失败时两个悬浮入口仍可拖、重置且不遮挡输入/返回。
- `ejs-router`: 先 EJS 后宏、单路由、变量读取次数、错误整段原样回退、无 include/partial。
- `i18n-visible`: 两个 locale 全键覆盖；错误/Toast/aria/空状态无裸用户文案。

以上门通过前，不建议继续把 v117 功能直接搬入当前 36 模块；应先把这些合同写入 117→Aster 蓝图与测试矩阵，再按模块责任逐步实现。
