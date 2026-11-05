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

官方接口完整清单见 `docs/official-api-coverage.json` 和控制台 API 调试目录，包括群管理、菜单、面板、素材、分片上传、流式消息和频道接口。`get_bot_list` 只返回该服务获准访问的 Bot，绝不返回 AppSecret。其余 Bot 相关请求必须带已授权的 `app_id`。

路径参数位于 `params`，如 `target`、`member_openid`、`guild_id`、`channel_id`、`panel_id`；请求体放在 `payload` 中。分页参数 `cursor`、`limit`、`before`、`after` 等位于 `params`。DELETE 接口支持官方定义的 JSON 请求体；频道日程查询的 `since` 按官方 SDK 发送为 JSON。原有 `send_message`、`upload_media`、`delete_message` 继续使用 `scope/target`。`delete_message` 支持频道及频道私信的 `hidetip`。所有请求均不自动重试。

成功时 `data` 保留官方 JSON。官方拒绝请求时返回 `success:false`、`error` 和 `official_response:{http_status,body,trace_id}`，保留官方业务码、说明及扩展字段，只隐藏访问令牌和 AppSecret。框架不预判 QQ 官方接口权限。连接中断等没有获得官方响应的情况，不伪造官方错误码；消息提交结果未知时仍保持隔离。

`send_stream_message` 使用 `scope:"c2c"`；`payload` 为官方流式分片参数，调用方沿用返回的 `stream_msg_id`，递增 `index`，明确指定 `msg_seq`，结束片使用 `input_state:10`。超时后不能换新请求 ID 自动重投。

`send_message` 支持 `msg_type:8` 图文卡片 `card:{type:"tuwen",content:{title,description,url,pic_url}}`；Markdown 的 `force_verify_image_resource`、`qqbot-media://` 图片引用和 `<qqbot-at-everyone />` 原样交给官方。素材上传顺序为 `prepare_media_image` → 用返回的预签名 URL PUT 图片（不携带 QQBot Authorization）→ `complete_media_image`；`get_media_images` 与 `delete_media_image` 管理已上传素材。群/私聊媒体分片接口分别由 `prepare_media_upload`、`finish_media_upload` 的 `scope` 选择。

Python SDK 提供 `context.api.call(action, **params)` 调用上述接口，AppID 绑定当前机器人；`send_stream_message` 提供流式分片入口。官方拒绝时保留原响应对象，不再统一替换为 `QQ API rejected request`。异常携带 `official_response`，未知发送继续抛出 `RPCError`，不能按明确失败重发。

0.4 增加 `publish_asset`（本服务数据文件发布为短期图片 URL）、`expose_http`（托管 IPC 进程的本机网页入口）、`registry_manage`（全局机器人注册表管理）和 `issue_login_ticket`（已授权管理员的私聊一次性登录）。后两者是高权限，必须单独授予；框架校验私聊发送者，不接受插件自报身份。服务配置及动作响应缓存均加密存储。登录凭据在权限、配置、令牌改变或服务停用后不可兑换。

IPC 进程获得 `OB_PLUGIN_DATA_DIR`，升级包不覆盖持久化数据。`upload_media` 可在 payload 中使用 `file_ref`，仅允许引用受信任 IPC 服务自己的数据文件，最多 8 MiB。图片发布需要在服务配置设置本站 HTTPS `public_base_url`。

托管插件可在 hello 中声明 `event: "lifecycle"`；框架先显示启动中，收到 `{"type":"runtime.status","event":"ready"}` 才显示已连接。业务初始化失败发送 `event: "error"` 后应退出，不能只完成管道握手就报告业务就绪。

请求 ID 按服务持久化。同一 ID、参数和授权上下文重复提交会返回原结果；参数或授权变化不允许复用 ID。服务重启后仍不重复执行已提交的请求。崩溃后结果未知的请求返回“结果未知”，不会自动再次执行。每服务默认每分钟最多 120 次 action；管理员可通过 `action_limit_per_minute` 设置 1–10000 的独立上限。

## 事件与确认

```json
{"type":"event","id":"42","app_id":"123456","event":"C2C_MESSAGE_CREATE","data":{"op":0,"t":"C2C_MESSAGE_CREATE","d":{"id":"message-id","content":"hello"}}}
```

插件处理完成后发送 `{"type":"event.ack","id":"42"}`。启用但断开的服务仍会积累授权范围内的事件；每次发送后等待 30 秒确认，最多发送 5 次。插件必须按事件 ID 做幂等。停止服务期间不接收新事件，重新连接只补发未确认事件。已撤销授权的历史事件不再投递。

服务默认采用 `delivery: "broadcast"`，作为独立订阅者接收事件，不阻断其他服务。

可选 `delivery: "handler"` 按同一 Bot、同一事件的 `priority` 从小到大处理，同优先级以服务 ID 排序。处理后发送 `{"type":"event.ack","id":"42","consumed":true}` 可阻止后续 handler 处理该事件；broadcast 服务不受影响。未确认或失败的前序 handler 不会被自动跳过，以免重复执行业务。重复确认不会修改已确认的消费结果。

`enabled: true, paused: true` 表示暂停执行并继续收件，不启动插件连接或进程；恢复后沿用原服务 ID 和持久化队列。`enabled: false` 表示停止，不再为该服务接收新投递。

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
- `TZ=Asia/Shanghai`、`OB_TIMEZONE=Asia/Shanghai`（托管进程的产品时区）

框架运行及页面展示默认东八区；数据库时间与协议时间戳继续按 UTC 保存，不改写历史数据。今日统计、聊天日期分隔、日期筛选、图表及新建定时任务使用东八区日界线。已显式指定其他时区的定时任务保持原设置。

运行中的服务需要先暂停或停止才能更新配置；暂停后保存仍保持暂停，不自动恢复执行。引用中的包不能删除。IPC 进程退出后显示异常，需要人工检查并重新启动，不进行无限进程重启。


## 指定机器人范围的登录

授予 `issue_login_ticket` 的可信服务可配置 `login_scope: "bot"`，将登录会话限制为凭据所属机器人。账号主人只可管理该账号及其插件业务设置，不能修改框架全局设置、进程权限或其他机器人。权限授予、业务管理员身份判断与具体登录指令由相应插件负责；框架负责凭据验证和会话范围检查。


## Action 排队与超时

`action` 帧可携带可选 `deadline`（Unix 毫秒时间戳）。框架将其限制在接收后的35秒以内；旧客户端未提供时使用同样的默认期限。过期且尚未开始的请求不会执行。各会话按 AppID、scope、target 保持顺序，不同会话通过有界分片队列并行处理；队列满时立即返回“未执行”，不会静默延后发送。事件确认及心跳不再等待慢 API 调用。

调用超时或明确标记结果未知时，不得换新请求ID盲目重发可能已经提交的消息。同一个请求ID及相同参数仍沿用既有幂等保障。框架不替插件决定动态、直播或上舰等业务事件的去重键。

平台管理员可在暂停服务的更新请求中明确传入 `trusted:true`，确认新的 `package_digest`，使替换期间继续保留 `enabled:true, paused:true` 的收件队列。未确认的新包仍不能执行；机器人主人无权利用此字段更换包或扩大权限。

## 插件图片缓存容量

`publish_asset` 对相同图片内容复用不可预测的公开地址，重复发布时续期24小时，避免不同会话重复占用缓存。缓存索引持久保存，旧图片地址继续有效；仅清理过期文件，不为新图提前删除尚未过期的图片。

默认总额度仍为512 MiB。磁盘有余量的部署可通过框架进程环境变量 `MENGKA_OB_PLUGIN_MEDIA_CACHE_MIB` 设置8至8192 MiB；未设置或无效值使用默认额度。此额度由部署管理员控制，插件配置无法扩大额度。达到额度时保留已有图片并明确拒绝新的发布请求，具体降级策略由插件决定。
