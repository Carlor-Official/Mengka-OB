# 萌卡OB

面向 QQ 官方机器人的自托管 Go 框架。统一管理多个 Bot，每个 Bot 独立选择 **WebSocket** 或 **Webhook**。

本仓库用于发布发行包、使用文档和接收问题反馈，前后端源码分别维护在私有仓库中。

当前处于开发阶段，尚未发布正式发行包。开发版本已提供首次部署初始化、多 Bot 管理、代理节点、官方接口调试、插件服务与导入、站点设置及邮件通知。真实 QQ Bot 的生产收发仍需进一步验收。

## 使用文档

- [部署与初始化](docs/deployment.md)
- [控制台菜单与官机功能](docs/console-navigation.md)
- [正文页 NT 布局基线](docs/frontend-nt-layout.md)
- [0.7.1 系统检视与优化](docs/system-review.md)
- [账号消息与登录设置](docs/account-features.md)
- [官方接口调试](docs/api.md)
- [插件服务与导入](docs/plugins.md)

请勿在 Issue 中提交 AppSecret、管理员密码、访问令牌、消息原文或数据库文件。

产品沿用萌卡 NT v2.6.0 前端的视觉与交互组件，业务层使用 QQ 官方机器人协议。设备指纹、NT 扫码登录、等级加速等非官方协议功能不属于萌卡OB。

插件作者可阅读 [obp/1 协议与包规范](docs/plugin-protocol.md)，以及 [IPC 示例](examples/ipc-echo/)。
