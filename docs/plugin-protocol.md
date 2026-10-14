# 萌卡OB 插件协议与包规范

协议：`obp/1`；清单：`mengka-ob/plugin@1`。这是新协议，不自动适配 NT、OneBot 或官机云旧插件。

## 两层连接

机器人与 QQ 平台之间使用官方 WebSocket 或 Webhook。插件与萌卡OB之间独立选择：

| 模式 | 建连方向 | 端点 |
| --- | --- | --- |
| `forward` | 插件连接框架 | 主 HTTP 服务的 `/plugin/ws/{serviceID}`，可通过 HTTPS 反向代理提供 WSS |
| `reverse` | 框架连接插件 | 管理员填写插件 WS/WSS 地址，框架负责断线重连 |
| `ipc` | 框架启动本机进程 | 标准输入与标准输出组成的双向管道，每行一帧 UTF-8 JSON；stderr 用于日志 |

三种模式共用下述消息、鉴权和权限，不使用管理员 Cookie 或管理员密钥。每个服务同一时刻只保留一个已鉴权连接，新连接替换旧连接。

## 握手与权限

正向 WS 和 IPC 插件先发：

```json
{"type":"hello","protocol":"obp/1","token":"该服务访问令牌"}
```

反向 WS 由框架先发送同一 `hello`，插件验证自己配置的令牌后回发 `hello`。令牌不放在 URL 中。

框架通过后返回 `hello.ok`，`data` 包含 `service_id`、`app_ids`、`permissions` 和 `config`。错误返回 `hello.reject` 并断开。

权限采用明确授权：未选 Bot、接口或事件即没有对应能力。`app_ids` 使用官方 AppID 字符串；`permissions.actions` 为接口名称数组，`permissions.events` 为事件类型数组，只有显式 `"*"` 才订阅所有事件。导入包的服务授权不能超出其清单声明。

更改配置和权限前必须停止服务。服务令牌仅在创建或重置时回显，数据库中加密保存；运行日志会过滤此令牌。停用会断开连接并终止框架托管的进程。

## 接口请求

```json
{"type":"action","id":"request-001","action":"send_message","params":{"app_id":"123456","scope":"group","target":"group_openid","payload":{"content":"你好","msg_type":0,"msg_id":"收到的消息ID"}}}
```

返回 `{"type":"action.result","id":"request-001","success":true,"data":{...}}`，失败时 `success:false` 并带 `error`。

可授权的官方接口包括原有 9 个 action 及 `ack_interaction`。`get_bot_list` 只返回该服务获准访问的 Bot，绝不返回 AppSecret。其余 Bot 相关请求必须带已授权的 `app_id`。

0.4 增加 `publish_asset`（本服务数据文件发布为短期图片 URL）、`expose_http`（托管 IPC 进程的本机网页入口）、`registry_manage`（全局机器人注册表管理）和 `issue_login_ticket`（已授权管理员的私聊一次性登录）。后两者是高权限，必须单独授予；框架校验私聊发送者，不接受插件自报身份。服务配置及动作响应缓存均加密存储。登录凭据在权限、配置、令牌改变或服务停用后不可兑换。

IPC 进程获得 `OB_PLUGIN_DATA_DIR`，升级包不覆盖持久化数据。`upload_media` 可在 payload 中使用 `file_ref`，仅允许引用受信任 IPC 服务自己的数据文件，最多 8 MiB。图片发布需要在服务配置设置本站 HTTPS `public_base_url`。

托管插件可在 hello 中声明 `event: "lifecycle"`；框架先显示启动中，收到 `{"type":"runtime.status","event":"ready"}` 才显示已连接。业务初始化失败发送 `event: "error"` 后应退出，不能只完成管道握手就报告业务就绪。

请求 ID 按服务持久化。同一 ID、参数和授权上下文重复提交会返回原结果；参数或授权变化不允许复用 ID。服务重启后仍不重复执行已提交的请求。崩溃后结果未知的请求返回“结果未知”，不会自动再次执行。每服务每分钟最多 120 次 action。

## 事件与确认

```json
{"type":"event","id":"42","app_id":"123456","event":"C2C_MESSAGE_CREATE","data":{"op":0,"t":"C2C_MESSAGE_CREATE","d":{"id":"message-id","content":"hello"}}}
```

插件处理完成后发送 `{"type":"event.ack","id":"42"}`。启用但断开的服务仍会积累授权范围内的事件；每次发送后等待 30 秒确认，最多发送 5 次。插件必须按事件 ID 做幂等。停止服务期间不接收新事件，重新连接只补发未确认事件。已撤销授权的历史事件不再投递。

外部插件为独立异步订阅者，不通过返回值阻断其他插件或 Bot 消息接收。

## 心跳与边界

框架每 15 秒发送 `ping`，插件应返回同 ID 的 `pong`。WS 连接超过 60 秒没有入站数据会断开。握手超时为 10 秒；单帧上限 4 MiB，服务配置上限 64 KiB。IPC 的 stdout 只能输出协议帧，诊断日志写入 stderr。

## 导入包

ZIP 根目录必须包含 `mengka.plugin.json`：

```json
{
  "schema":"mengka-ob/plugin@1",
  "id":"example-echo",
  "name":"示例回复插件",
  "version":"1.0.0",
  "protocol":"obp/1",
  "transport":"ipc",
  "description":"按官方消息事件回复测试指令",
  "entrypoints":{
    "windows/amd64":{"path":"echo.exe"},
    "linux/amd64":{"path":"echo"}
  },
  "permissions":{
    "actions":["send_message"],
    "events":["GROUP_AT_MESSAGE_CREATE","C2C_MESSAGE_CREATE"]
  }
}
```

入口可指定 `args` 数组；不拼接 Shell 命令。`runtime` 默认为 `native`，也可选择 `node`、`python`，此时入口是包内脚本并由本机已安装的相应运行时执行。跨平台脚本可使用 `"any":{"runtime":"python","path":"main.py"}`。

ZIP 最大 32 MiB，解压总量最大 128 MiB，最多 512 项。拒绝路径穿越、绝对路径、大小写重名、符号链接、特殊文件和缺失入口。按 ZIP SHA-256 保存独立目录，新版本不覆盖旧版本。

**导入仅校验和保存，不运行程序。** 创建服务后，由管理员选择 Bot 与权限；启动本机包时需要明确确认可信来源。以当前操作系统账号运行，进程隔离不等于安全沙箱。启动器不继承管理员密钥等敏感环境变量，只传递基本运行环境和：

- `OB_PLUGIN_PROTOCOL`、`OB_PLUGIN_TRANSPORT`
- `OB_PLUGIN_TOKEN`、`OB_PLUGIN_SERVICE_ID`
- `OB_PLUGIN_URL`（WS 模式端点）

运行中的服务需要先停止才能更新配置。引用中的包不能删除。IPC 进程退出后显示异常，需要人工检查并重新启动，不进行无限进程重启。
