# 双轨仪表盘与 Holo Veil 设计合同（r002）

本文件吸收旧 Selected UI 设计稿中仍有效的职责；旧稿的默认人物立绘、旧素材路径、旧部署凭证与旧测试计数均已退役。机器合同位于 `blueprint/contracts/orbit/` 与 `blueprint/contracts/social/`。

## 双轨仪表盘

- 永远只有内圈、外圈两条轨道；新注册入口进入现有轨道的排序/背面队列，不创建第三轨。
- `activeId` 是稳定身份，索引只从当前排序推导。拖动结束吸附到一个有效入口；拖动后的合成 click 必须被抑制。
- 内圈承载队伍、遭遇、检定、法术、地图标记；外圈承载背包、任务、通讯、关注及 Mod 入口。
- 世界球、家园场景属于可替换场景资源；按钮、轨道、路线、点位、边框和焦点状态由 DOM/CSS/SVG 负责。
- 玩家头像、立绘与社交侧栏人物均为空语义槽，只能由世界 Mod 或用户资源显式注入。

## Holo Veil 社交

- 消息、论坛、直播和自定义 section 共用一个 `world-social` 根；index/detail 在同一根内切换，不创建 thread overlay。
- 所有宽度保持纵向 section rail；超过五个直达 section 时使用真实“更多”入口。
- 每个 section 独立保存 query、filter、sort、scroll；进入详情再返回时恢复来源状态。
- `unread`、`followed`、`online`、`kind`、`status` 是互相独立的字段，不由图标或颜色反推。
- 场景媒体只能作为内容背景；人物槽缺省为空，不以裁切图或默认立绘填充。

## 视觉与无障碍

- 颜色、间距、轨道参数与最小触控尺寸以 `design-tokens.json` 为机器真源。
- 图标使用语义 ID，文件短名只属于存储层；SVG 内部 ID 不因物理改名而变化。
- 交互控件保持真实 button/input 语义、可见 focus、44px 最小目标，并支持 reduced motion。
- 394px 手机边界是第一验收尺寸；宽屏是同一结构的扩展，不另造一套导航。

## 来源与证据边界

- 94 个现行视觉文件的来源路径、短路径、用途、字节与 SHA-256 见 `assets/catalog.json`。
- 旧人物源图、人物 WebP、设计 mockup 与旧部署回读只在逐文件处置账中留哈希和决策，不进入 r002 当前包。
- 浏览器门或 Tavo 真机门显示 SKIP/PENDING 时不得表述为通过。
