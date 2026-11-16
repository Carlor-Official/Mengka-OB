# QQ 官方接口适配（2026-11-16）

对照 QQ 官方文档 v1.50.0 和 20261116 变更记录完成源码适配，对应框架发行版为 1.0.4。

## 新增

- 新增用户资料接口 `get_user_info`，对应 `GET /v2/users/{user_openid}/info`。控制台“用户资料”填写用户编号即可查询；Python SDK 提供 `context.api.get_user_info(user_openid)`。
- 保留官方响应中的用户昵称、头像、统一用户标识、主动消息偏好及扩展字段。官方拒绝时继续返回原业务码和说明。
- 接收单聊消息中的昵称、头像和群消息中的群内昵称、头像。群昵称用于聊天及引用消息显示，按机器人、群和成员分别保存。
- 接收群事件中的 `union_group_openid`，在群联系人和 SDK 中提供关联信息；保持发送群编号和各机器人数据独立。

## 调整

- 自动补全昵称时，已确认的单聊用户通过官方用户资料接口查询。群成员编号继续使用群成员资料接口；既有群接口错误冷却不会阻止单聊资料查询。
- SDK 在群消息缺少显式 `author.id` 时优先使用成员编号，单聊优先使用用户编号；已有显式编号保持兼容。
- 更新官方接口覆盖表、SDK 说明和调试目录文档日期。已核对先前的图文卡片、素材引用、艾特全体及按钮颜色能力。

## 修复

- 修复查询指令面板列表丢失必填 `scope` 的问题；前端按名称选择单聊、群聊、文字子频道或频道私信，SDK 同样支持传入。
- 修复不同群昵称串用，以及官方明确清空群昵称后仍显示旧值的问题；旧事件未包含该字段时保留已知值。
- 资料补全的迟到响应只填补缺失资料，不覆盖新事件提供的值；群昵称完全由事件维护。

## 验证

- Go 全量测试及 `go vet ./...`；官方接口路由与覆盖表对照。
- SDK 9 项回归，覆盖资料响应、官方错误、机器人绑定、面板场景及新旧事件兼容。
- 前端 270 项测试、168 个 Vue 文件绑定检查及生产构建。
- 本地模拟接口浏览器验证，覆盖用户编号保真、官方错误显示、面板场景和 1440/375 宽度。没有向真实 QQ 发送测试消息；实际账号的接口权限和官方结果需在部署后验证。

## 官方依据

- [变更记录](https://bot.q.qq.com/wiki/develop/api-v2/changelog.html)
- [获取用户基本信息](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_users_user_openid_info.get.html)
- [单聊消息事件](https://bot.q.qq.com/wiki/develop/api-v2/autogen/event/c2c_message_create.html)
- [群聊消息事件](https://bot.q.qq.com/wiki/develop/api-v2/autogen/event/group_message_create.html)
- [群成员退出事件](https://bot.q.qq.com/wiki/develop/api-v2/autogen/event/group_member_remove.html)
- [获取群基本信息](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_groups_group_openid_info.get.html)
- [查询指令面板列表](https://bot.q.qq.com/wiki/develop/api-v2/autogen/api/v2_panels.get.html)
