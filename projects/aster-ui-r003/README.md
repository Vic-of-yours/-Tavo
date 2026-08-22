# Aster UI R003 · 单次落位候选

本目录承接 `projects/aster-117-blueprint` r002，并加入当前 Aster 0.9.1 的可安装包、完整源码包和本轮 UI 核对证据。它不是 Tavo 已部署声明。

## 本轮修正

- 小手机：`aster.phone.core@2.5.0`；仅一条状态栏；时间/节日在状态栏，地点/日期/季节在世界组件；桌面 pages 与 Dock 中的 app id 互斥；v1 布局自动迁移到 v2；保留 ○/×/△。
- 仪表盘：`aster.dashboard.world@4.2.0`；世界名绑定 `world.label`；玩家在线副本移除；单一星体、单一 SVG 路线、单一地点板、两条轨道、单一玩法 stage。
- 表面：`aster.skin.shell@4.2.0`；dashboard root alpha 0.85；铺满安全 viewport；三完整伴星 + 右侧约 38% preview。
- 生命周期：`aster.panel.registry@1.3.0` 支持 singleton alias；phone、dashboard、world-social 互相替换，`world-dashboard` 不再产生第二个根。
- 自包含：四项制作源和三张本轮示意/参考证据已进入 source ZIP；单独下载本目录即可恢复施工与复验。

## 交付

| 文件 | SHA-256 |
|---|---|
| `release/Aster-mobile-shell-0.9.1.zip` | `678d004b291760ef9cc4fb98d19b223b40bd70fbf10871d8413a7498d0388323` |
| `release/Aster-mobile-shell-source-0.9.1.zip` | `1196eb6c41b36f3383dfa745c7825316a63cfb3c036b6993ee7869898d56711a` |

安装包含五书、Runtime 0.9.1、Mod Importer 1.4.0、common assets 1.0.0 与 orbit/holo assets 1.1.0。源码包包含源码、测试、工具、设计合同、制作源、参考证据和回归报告。

## 验证状态

- Five Books：19 / 5 / 1 / 5 / 6
- First Gate：762 PASS
- Importer：7 PASS
- Mod Importer：281 PASS
- UI Contracts：11 PASS
- Common Assets：840 PASS
- Orbit/Holo Assets：188 PASS
- ZIP CRC 与发布/交付 SHA-256：PASS
- Playwright Chromium：SKIP（执行器未安装）

因此本目录是可恢复、可安装的 R003 候选，但不是正式浏览器放行或当前 Tavo 回读证据。正式发布仍需真实 Chromium 通过和 Tavo 写入后精确回读。
