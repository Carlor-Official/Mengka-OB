# 聊天富消息与完整原始记录

聊天界面解析引用回复、多张图片、GIF、语音、视频、文件、Markdown、分享卡片及内嵌完整内容的合并转发。合并记录每次展开 30 条，可继续查看全部；大于 256 KiB 的消息单独点击加载，服务端不截断原文。

官方 `message_type=103` 的 `msg_elements` / `parallel_message` 作为引用处理，不能误判为合并转发。仅有摘要或 resid 的转发明确提示缺少完整内容，不调用 NT 普通 QQ 私有协议伪装兼容。旧版转发已经丢失的字段不会自动恢复，除非源日志仍保留且单独补录。

语音优先使用官方 `voice_wav_url`，否则获取原附件。SILK 使用固定版本 Go 解码器在独立子进程转为 WAV，限制输入 16 MiB、音频 5 分钟、并行 2 个任务；超时、无效文件、非公网地址明确报错。其他浏览器原生支持的音频直接播放。网络 URL 与过期权限仍受源站限制。

完整 JSON 与展示数据分别加密存储，跟随消息日志保留 30 天。展示层隐藏一次性登录凭据；管理员原始记录接口保留未经展示加工的内容。所有接口受现有控制台认证及 Bot 隔离保护：

- `GET /api/v1/accounts/{appid}/console/chat/original/{journal_id}`：完整原始 JSON。
- `GET /api/v1/accounts/{appid}/console/chat/detail/{journal_id}`：完整展示数据。
- `GET /api/v1/accounts/{appid}/console/original-events`：最近 100 条原始事件索引。
- `GET /api/v1/accounts/{appid}/console/original-events/{id}`：包含非消息事件的原始 JSON。
- `GET /api/v1/accounts/{appid}/console/chat/voice/{journal_id}?path=attachments.0`：只从该 Bot 已存消息指定附件获取音频，不接受外部任意 URL 参数。

云平台插件 v2 载荷保留 `official_event` 和 `outbound_request`，未知字段不删除、长正文不裁剪。接收上限 16 MiB，超限整条拒绝并返回 413。转发入口只记账，不执行自动回复或插件；安装插件不会改变官方开放平台原回调。
