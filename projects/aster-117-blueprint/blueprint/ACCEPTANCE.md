# 117→Aster 蓝图 r002 放行矩阵

## 已完成的静态/本地门

- 当前清理树逐文件进入 Code 或 Assets r002；包清单逐项记录路径、字节与 SHA-256。
- 代码包和素材包各自无精确重复，跨包成员哈希交集为 0，且无嵌套压缩包。
- 36 个当前实现模块 ID 唯一；五书构建、导入器、Mod 导入器、首门和 UI 合同测试通过。
- 94 个视觉文件分类、短名、格式、尺寸、SVG 引用、非人物分类与运行注册表静态对应通过。
- 所有输入文件表示进入 `manifests/full-file-disposition.json`，未知处置为 0。

## 校准中，不得宣称完成

- 86 个目标模块仍是候选架构；其中 21 个没有 v117 迁移账直接 target。
- `implementedVerified` 仍为 0；占位 acceptance 词不构成 Aster 实现证据。
- loader 的“静态入 TPG”与“签名/哈希 allowlist”尚未最终选定。
- 25 panel、16 App、62 参数与两个参考插件仍缺逐项产品验收轨。
- Playwright 两个真实浏览器门与 Tavo 真机安装/readback 尚未执行。
- 原始四附件并未全部作为可恢复字节保存到 Git；Git 完整性只覆盖 r002 当前交付树与 Git 已提交内容。
