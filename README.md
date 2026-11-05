# 萌卡OB

面向 QQ 官方机器人的自托管 Go 框架。统一管理多个 Bot，每个 Bot 独立选择 **WebSocket** 或 **Webhook**。

本仓库用于发布发行包、使用文档和接收问题反馈，前后端源码分别维护在私有仓库中。

当前正式版为 **1.0.1**。[下载正式版安装包](https://github.com/Carlor-Official/Mengka-OB/releases/tag/v1.0.1)；支持 Windows amd64、Linux amd64 和 Linux arm64。无需注册卡或验证端账号，首次启动直接初始化自己的管理员；安装包不包含预设账号、机器人配置、业务插件包或插件数据。

已提供可视化聊天、引用与富消息展示、多 Bot 管理、官方接口调试、插件服务与导入、站点设置、邮件通知、独立版本检查、一键重启与强制更新。验证端分别管理萌卡 NT / 萌卡 OB 版本；OB仅同步版本策略。请先使用测试 Bot 验收自己的权限、网络和业务收发。

## 使用文档

- [1.0.1 正式版说明](docs/release-readme.txt)

- [QQ 表情与消息模板发送](docs/qq-faces-and-template-send.md)
- [实时聊天、会话筛选与昵称查询](docs/chat-realtime-and-profiles.md)
- [聊天图片缓存与 Markdown 按钮](docs/chat-images-and-buttons.md)
- [部署与初始化](docs/deployment.md)
- [Markdown 发送与分屏实时预览](docs/markdown-preview.md)
- [聊天富消息与完整原始记录](docs/chat-rich-messages.md)
- [1.0.1 更新与升级说明](docs/releases/1.0.1.md)
- [免卡初始化与独立版本检查](docs/algorithm-integration.md)
- [在线更新、低版本强制更新与重启](docs/runtime-update.md)
- [控制台菜单与官机功能](docs/console-navigation.md)
- [正文页 NT 布局基线](docs/frontend-nt-layout.md)
- [0.7.1 系统检视与优化](docs/system-review.md)
- [账号消息与登录设置](docs/account-features.md)
- [官方接口调试](docs/api.md)
- [插件服务与导入](docs/plugins.md)

请勿在 Issue 中提交 AppSecret、管理员密码、访问令牌、消息原文或数据库文件。

产品沿用萌卡 NT v2.6.0 前端的视觉与交互组件，业务层使用 QQ 官方机器人协议。设备指纹、NT 扫码登录、等级加速等非官方协议功能不属于萌卡OB。

插件作者可阅读 [obp/1 协议与包规范](docs/plugin-protocol.md)，以及 [IPC 示例](examples/ipc-echo/)。
