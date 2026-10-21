# 实时聊天、会话筛选与昵称

聊天页通过已认证的 `/api/v1/accounts/{appid}/console/chat/events` 接收 SSE 变更通知，读取当前机器人的会话快照。收信、发信、撤回、修改资料和昵称补全都会通知页面。通知不携带聊天内容，积压时合并；断线重连后重新读取，15 秒定时补拉兜底。切换机器人或离开页面会注销连接，登录失效后服务端关闭连接。

左侧提供全部、群聊、私聊与文字搜索。频道归入群聊，频道私信归入私聊；只有群成员记录、没有私聊消息的用户不会成为私聊会话。浏览历史时保持位置，并显示新消息提示；最新消息附近跟随滚动。聊天记录排除好友添加等控制事件，原始事件日志保留。

名称优先使用已保存资料，再使用消息中的 `author.username` / `author.nickname`；占位名称不会盖住后来获得的昵称。昵称补查在账号设置中控制，查询与缓存直接内置于 Go 框架。仅对该机器人实际观察到的群与成员关系请求腾讯的 `GET /v2/groups/{group_openid}/members/{member_openid}`，不互换或猜测 C2C、member、union OpenID。已有名称和人工备注不被空结果覆盖。查询失败按用户退避；业务码 11253 按机器人暂停一小时，避免重复请求无权限接口。

2026-10-21 实测：测试服机器人对此接口返回 HTTP 400、业务码 11253（应用无接口访问权限）。只有取得相应官方权限后，此路径才能补全该机器人的未知群成员昵称。仅有私聊 OpenID、没有可用群成员关系或昵称事件时，当前没有验证可用的官方直接查询路径；保留占位名称或人工备注，不能承诺仅自建服务即可获取全部昵称。

参考并核对了 [ElainaBot_v2 的群成员查询实现](https://github.com/ElainaCore/ElainaBot_v2/blob/main/core/message/sender.py)。腾讯文档中的 [频道成员详情](https://github.com/tencent-connect/bot-docs/blob/main/docs/develop/api-v2/server-inter/channel/role/member/get_member.md) 是频道接口，不能直接替代群或 C2C 查询。

云平台原有 `i.elaina.vin/api/bot/xx.php` 在线实测返回 404，当前实现不再调用它。经用户明确授权，使用测试服一条用户记录实测 [OIAPI Openid 接口](https://oiapi.net/index/doc?id=113)，获得 HTTP 200、业务码 1 与昵称。因此新增账号设置“昵称查询来源”：默认仅官方接口，可主动切换为“官方优先，OIAPI 备用”。备用查询只发送 AppID 和 OpenID，验证返回 OpenID 与请求一致，只保存昵称；不保存年龄、气泡等返回资料。单次请求最长 5 秒，单用户失败一小时后重试，第三方失败增加全局短暂退避。已有资料、事件昵称和人工备注优先。
