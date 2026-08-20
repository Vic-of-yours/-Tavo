# 素材蓝图入口（r002）

现行运行素材统一位于 `assets/`，共 94 个视觉文件和 3 个元数据文件。目录按用途分为导航/操作/状态/世界/社交/内容/开发/HUD 图标、遮罩、SVG 合集、纹理、动效、壁纸、场景和地图。

- `assets/catalog.json`：94 行新旧路径、用途、语义键、公开 ID、短存储名、尺寸与 SHA-256。
- `production-tasks.json`：通用 UI 素材的生产规格与短名。
- `common-ui.svg`：通用 UI 结构蓝图，不是运行素材。
- `AUDIT.md`：保留/剔除边界及语义相似关系。
- `ACCEPTANCE.md`：素材放行门。
- `blueprint/contracts/assets/integration.json`：资源接入边界。

人物、头像、服装差分与默认角色站姿不属于基础素材包。相关语义槽保留为空，由世界 Mod 或用户资源注入。
