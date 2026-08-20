# 素材来源与派生关系（r002）

`assets/catalog.json` 的 `legacyPath` 与 SHA-256 是当前包内每个视觉文件的可验证来源索引。r002 只做分类和改名；94 个视觉文件的字节与 r001 哈希集合完全相同。

来源边界：

- 通用图标、遮罩、纹理、壁纸与动效来自 Projects 当前 Aster 工作区的通用 UI 素材树。
- HUD 图标、世界球、家园及社交媒体场景来自 Projects 当前 Aster 工作区的 Orbit/Holo 素材树。
- 世界地图来自 Projects 当前 Aster 工作区的 world-dashboard 素材树。
- `scenes/city.webp` 与 `scenes/station.webp` 是地图母图的内容裁切；`scenes/qa.webp` 是家园母图的内容裁切。它们不是精确重复，分别服务固定卡片用途。
- 玩家立绘、站姿、开放人物源图和参考插件人物封面已剔除；其原始哈希与处置见 `manifests/full-file-disposition.json`。

四个用户来源/参考件没有提供足以独立验证的统一上游仓库与许可证声明。r002 不据此新增版权结论；对外再分发前仍需用户确认各素材的授权范围。
