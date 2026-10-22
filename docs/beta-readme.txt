萌卡OB 1.0.6beta 内测版（内部版本：1.0.6-beta）

本版修复 CVE-2026-111943，三个平台均使用 Go 1.26.10 重编译。
必须更新框架程序并重启，单独更新前端或服务器 Go 安装不能修复旧程序。
原生 Markdown 模板可用输入框覆盖正文；官方参数模板请在模板配置中修改参数。
聊天工具栏选择 Markdown 后可实时预览；Enter 换行，Ctrl+Enter 或按钮发送。
聊天列表支持全部、群聊、私聊筛选；新消息实时更新，阅读历史时保留位置。
昵称查询默认仅使用官方接口。缺少腾讯群成员查询权限时，可在账号设置主动选择
“官方优先，OIAPI 备用”。备用线路仅发送 AppID 和用户 OpenID，不发送密钥或聊天内容。
已有昵称优先保留，缺失资料分批查询；第三方服务未提供结果时仍保留用户标识。
已过期且从未缓存的旧图片无法恢复；新消息中的受支持 QQ 图片会提前缓存。

首次使用
1. 将整个压缩包解压到独立目录，保留 web/dist 与程序的相对位置。
2. Windows：在解压目录运行 mengka-ob.exe。
   Linux：进入解压目录，运行 chmod +x mengka-ob && ./mengka-ob。
3. 本机打开 http://127.0.0.1:18080；服务器部署打开 http://服务器公网IP:18080。
   阅读协议并设置自己的管理员账号和密码。
4. 框架自动向算法系统登记 OB 账号；接入就绪后添加自己的官方机器人。

服务器部署
默认监听全部网卡。云安全组与系统防火墙需放行 TCP 18080（或自己设置的端口）。
只需要本机反向代理连接时，可使用：
  ./mengka-ob -listen 127.0.0.1:18080 -data ./data -web ./web/dist
反向代理域名配置公网 HTTPS 后，复制账号页给出的 Webhook 回调地址到 QQ 开放平台。
反向代理必须保留原域名 Host（Nginx 使用 proxy_set_header Host $http_host），
不要设置成 localhost；同时转发 WebSocket Upgrade、关闭 SSE 响应缓冲。
WebSocket 与 Webhook 由每个 Bot 独立配置。部分 AppID 需要在开放平台配置服务器出站 IP 白名单。
公网 IP＋端口可直接打开管理页；官方 Webhook 回调仍要求 HTTPS。
未指定 -listen 时，初始化保存的端口在重启后生效；显式 -listen 优先。
可用 MENGKA_OB_LISTEN_HOST 限制监听网卡而不覆盖保存端口。
完整包从其他目录启动时默认使用程序旁的 data 与 web/dist。
详细部署和 systemd 示例：https://github.com/Carlor-Official/Mengka-OB/blob/main/docs/deployment.md

升级与备份
保留并备份整个 data 目录（包括 master.key），不要复制其他用户的 data 或管理员配置。
1.0.0-beta 订阅 OB 内测更新通道，能够更新后续 beta 及正式版；正式版不会自动切换至 beta。
低于算法系统设置的 OB 最低版本时会强制更新，进度、失败重试和完成结果由弹窗显示。
0.9 及更早开发版本首次升级到 beta 请停止旧程序后手动替换程序与 web/dist，保留 data。
不要同时启动两个实例使用同一份 data；不要复用萌卡NT的数据目录。

内测范围
多 Bot 管理、官方 WebSocket/Webhook、正向/反向 WS 与 IPC 插件服务、导入插件、配置管理、
算法授权、一键重启和在线更新。新增可视化聊天、引用、图片、合并转发与语音播放，
机器人头像和会话时长，以及 HTTP IP＋端口下的交互兼容修复。
插件使用 OB 新协议，不直接兼容 NT 插件二进制。
真实 QQ Bot 收发取决于开放平台权限、网络和应用配置，请先使用测试 Bot 验收自己的业务。

发行包不附带机器人、管理员账号、登录令牌、生产数据库或源码。
问题反馈：https://github.com/Carlor-Official/Mengka-OB/issues
不要提交 AppSecret、密码、令牌、数据库和包含私人消息的日志。
