# 官方接口调试

控制台“接口调试”使用管理员会话请求 `POST /api/v1/debug/request`：

```json
{
  "service_id": 1,
  "timeout_seconds": 30,
  "request": {
    "type": "action",
    "id": "example-1",
    "action": "get_bot_list",
    "params": {}
  }
}
```

| action | 参数 |
| --- | --- |
| `get_bot_list` | 无，返回配置与状态，不返回 AppSecret |
| `get_version_info` | 无 |
| `get_bot_status` | `app_id` |
| `get_me` | `app_id` |
| `get_guilds` | `app_id` |
| `get_channels` | `app_id`, `target`（频道服务器 ID） |
| `send_message` | `app_id`, `scope`, `target`, `payload` |
| `upload_media` | `app_id`, `scope`（group/c2c）, `target`, `payload` |
| `delete_message` | `app_id`, `scope`, `target`, `message_id` |

AppID、OpenID 和消息 ID 都使用字符串。消息场景 `scope` 支持 `group`、`c2c`、`channel`、`direct`。

消息 `payload` 使用 QQ 官方字段，例：`{"content":"你好","msg_type":0,"msg_id":"收到的消息ID"}`。Markdown、按钮和媒体字段也通过原始 JSON 传入，权限、格式、限额以 QQ 官方响应为准。

返回的 `action_result.success` 表示本次动作是否成功，不能只根据 HTTP 200 判断业务结果。发送超时或服务器返回不确定结果时，不自动重发消息，应先核对会话。

参考：[QQ 官方机器人文档](https://bot.q.qq.com/wiki/develop/api-v2/)。
