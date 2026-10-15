萌卡OB 1.0.0beta 内测版（内部版本：1.0.0-beta）

首次使用
1. 将整个压缩包解压到独立目录，保留 web/dist 与程序的相对位置。
2. Windows：在解压目录运行 mengka-ob.exe。
   Linux：进入解压目录，运行 chmod +x mengka-ob && ./mengka-ob。
3. 打开 http://127.0.0.1:18080，阅读协议并设置自己的管理员账号和密码。
4. 框架自动向算法系统登记 OB 账号；接入就绪后添加自己的官方机器人。

服务器部署
默认仅监听本机。需要反向代理时，可使用：
  ./mengka-ob -listen 127.0.0.1:18080 -data ./data -web ./web/dist
反向代理域名配置公网 HTTPS 后，复制账号页给出的 Webhook 回调地址到 QQ 开放平台。
WebSocket 与 Webhook 由每个 Bot 独立配置。部分 AppID 需要在开放平台配置服务器出站 IP 白名单。
如需远程访问内测界面，可在私有网络部署或自行配置 HTTPS 反向代理。

升级与备份
保留并备份整个 data 目录（包括 master.key），不要复制其他用户的 data 或管理员配置。
1.0.0-beta 订阅 OB 内测更新通道，能够更新后续 beta 及正式版；正式版不会自动切换至 beta。
低于算法系统设置的 OB 最低版本时会强制更新，进度、失败重试和完成结果由弹窗显示。
0.9 及更早开发版本首次升级到 beta 请停止旧程序后手动替换程序与 web/dist，保留 data。
不要同时启动两个实例使用同一份 data；不要复用萌卡NT的数据目录。

内测范围
多 Bot 管理、官方 WebSocket/Webhook、正向/反向 WS 与 IPC 插件服务、导入插件、配置管理、
算法授权、一键重启和在线更新。插件使用 OB 新协议，不直接兼容 NT 插件二进制。
真实 QQ Bot 收发取决于开放平台权限、网络和应用配置，请先使用测试 Bot 验收自己的业务。

发行包不附带机器人、管理员账号、登录令牌、生产数据库或源码。
问题反馈：https://github.com/Carlor-Official/Mengka-OB/issues
不要提交 AppSecret、密码、令牌、数据库和包含私人消息的日志。
