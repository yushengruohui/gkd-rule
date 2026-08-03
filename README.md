# GKD Rule

这是 [GKD](https://gkd.li/) 订阅规则仓库，用于维护应用内广告、弹窗等界面的自动跳过规则。

## 订阅地址

将以下地址复制到 GKD 中添加订阅：

```text
https://raw.githubusercontent.com/yushengruohui/gkd-rule/main/dist/gkd.json5
```

若无法访问 GitHub Raw，可使用 jsDelivr：

```text
https://fastly.jsdelivr.net/gh/yushengruohui/gkd-rule@main/dist/gkd.json5
```

## 本地开发

项目要求 Node.js 22 或更高版本（仓库使用 Node.js 24）和 pnpm 10。

```shell
git clone https://github.com/yushengruohui/gkd-rule.git
cd gkd-rule
pnpm install
```

常用命令：

```shell
pnpm format # 格式化代码
pnpm lint   # 修复 ESLint 问题
pnpm check  # 类型检查并校验订阅规则
pnpm build  # 校验并生成 dist/gkd.json5
```

## 规则目录

- [订阅信息](./src/subscription.ts)
- [规则分类](./src/categories.ts)
- [全局规则](./src/globalGroups.ts)
- [应用规则](./src/apps)

每个应用使用其 Android 包名作为文件名，例如 `src/apps/com.tencent.mm.ts`。新增或修改规则后，请运行 `pnpm check` 确认规则有效；构建产物位于 `dist/`，无需手动编辑。

## 贡献

提交规则时请尽量提供可复现的界面截图或录屏，并确保选择器只匹配目标页面，避免影响应用的正常操作。GKD 规则 API 可参考 <https://gkd.li/api>。
