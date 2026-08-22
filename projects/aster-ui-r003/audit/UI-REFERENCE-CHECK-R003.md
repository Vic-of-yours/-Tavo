# 当前 UI 核对记录 · R003

日期：2026-08-22  
范围：小手机、世界仪表盘、同一可见状态的单次落位。

## 证据优先级

发生冲突时按以下顺序裁决，低优先级材料只补充气质与问题证据，不反向覆盖高优先级合同。以下相对路径均以 `design/orbit-holo-veil/` 为根：

1. 选定 mockup 与冻结蓝图：`mockups/dashboard-p1-double-orbit.png`、`blueprint/01`、`02`、`04`、`05` 及 `contracts/design-tokens.json`。
2. 参考图：`reference-evidence/dashboard-reference.png`、`reference-evidence/messages-reference.png`；只吸收冷色玻璃、长页信息层次、地图阅读关系和光幕气质。
3. 现状图：`reference-evidence/phone-current.jpg`；只用于识别壳体偏宽、空区过大和时间 / 节日重复，不作为新增布局真源。

以上三张参考 / 现状证据均已纳入当前 source，路径与 SHA-256 由 `ASSET-MANIFEST.json` 固定；单独 source ZIP / Git clone 不依赖工作区外文件即可复核。

## 最终落位

| 表面 | 最终视觉与信息位置 | 单次落位约束 |
|---|---|---|
| 小手机外壳 | 瘦长、冷感、细边与低亮玻璃；壳体只由 Skin 绘制 | System 不持有 CSS；手机与仪表盘不能同时可见 |
| 手机状态栏 | 左 `worldTime`，中 `ASTER // PHONE`，右 `festival` | 组件不再重复时间、节日 |
| 手机身份行 | `userName` + `world.label` | 组件不复制身份信息 |
| 手机世界组件 | `location` 主标题；`worldDate` + `season` 辅助信息 | 不显示 `worldTime`、`festival` |
| 手机应用区 | 每个 app id 在当前桌面页或 Dock 二选一 | 新布局与 v1 迁移后都必须满足 pages ∩ dock = ∅，桌面页间也不得重复 |
| 仪表盘根 | 占满可用 viewport；玻璃根 alpha 固定 `.85`（约 15% 背景透过） | 不保留 560px 桌面浮窗或第二层近不透明背板 |
| 仪表盘顶栏 | `world.label`、世界在线、日期、时间 | 不再添加 timebar、页脚副本；世界在线与联系人在线分语义 |
| 玩家层 | 玩家名、等级、HP、EN、四属性与开放立绘 | 不复制到世界指标或玩法层 |
| 世界地图层 | 单一星体背景 + 独立 DOM 点位 + 单一 SVG 路线 + 单一 active 地点牵引板 | 背景位图不得烘焙点位 / 路线；不得生成第二张地点卡 |
| 双轨入口 | inner 5 个玩法命令；outer 4 个世界路由 | 恰好两圈；同一路由不得在仪表盘内再次出现 |
| 玩法层 | 单一 switcher + 当前 stage | 只渲染当前玩法指标与动作 |
| dashboard alias | `dashboard` 为 canonical singleton；`world-dashboard` 仅委托它 | 任一路径打开后只能有一个 dashboard root |

## 判定边界

- 透明度数值以合同中的 alpha `.85` 为准；“85% 透明”在本轮解释为 85% 不透明、约 15% 透底。
- 本记录是施工核对合同，不替代真实浏览器截图、自动测试或 Tavo 写回 / 回读证据。
- Runtime 与发布包当前目标版本为 `0.9.1`；历史 `0.9.0` 在线回读记录保持历史属性，不据此声称 R003 已部署。
