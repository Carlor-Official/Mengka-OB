# 部署与初始化

## 下载安装

从 [Releases](https://github.com/Carlor-Official/Mengka-OB/releases) 下载对应 Windows amd64、Linux amd64 或 Linux arm64 安装包，完整解压到独立目录。当前内测版为 `1.0.6-beta`。

Windows 运行 `mengka-ob.exe`。Linux 进入解压目录后运行：

```sh
chmod +x mengka-ob
./mengka-ob
```

默认监听所有网卡的 TCP **18080** 端口，本机访问 `http://127.0.0.1:18080`，服务器部署访问 `http://服务器公网IP:18080`。不需要先配置域名才能打开管理页面。服务器云安全组和操作系统防火墙均需放行相同的 TCP 端口；Windows 首次启动也需允许相应网络的入站访问。

首次访问按页面完成协议确认、管理员账号和密码初始化。正式添加 Bot 前应先完成自己的管理员配置。

## 端口与地址优先级

1. 显式 `-listen` 同时指定监听地址和端口，优先于保存的端口和环境变量。
2. 没有 `-listen` 时，使用初始化保存的端口；新安装默认 18080。初始化修改端口在下次启动或框架重启后生效。
3. 没有 `-listen` 时，`MENGKA_OB_LISTEN_HOST` 可以限制监听网卡；默认不设，监听全部网卡。仅配置这个变量不会覆盖保存的端口。

对公网直连，可直接使用默认启动方式，或明确指定：

```sh
./mengka-ob -listen 0.0.0.0:18080
```

只允许本机反向代理连接时使用：

```sh
./mengka-ob -listen 127.0.0.1:18080
```

`1.0.0-beta` 原包默认监听 127.0.0.1，外网无法直连。旧版本可先用 `-listen 0.0.0.0:18080` 临时解决，再升级 1.0.1beta。升级后若 systemd、启动脚本仍明确指定回环地址，框架会尊重该配置；需要直连时应修改自己的启动参数。

## 数据与前端目录

完整安装包的默认 `data`、`web/dist` 相对于程序目录解析，从其他目录运行绝对路径或创建快捷方式不会另建一份空配置。源代码开发目录仍支持工作目录默认值。

旧版若已在当前工作目录生成 `data/platform.db`，而程序目录没有数据库，会继续使用旧数据；两处均有数据库时启动会要求用 `-data` 明确选择。显式相对路径按当前工作目录解析，后台部署建议使用绝对路径：

```sh
/opt/mengka-ob/mengka-ob -data /opt/mengka-ob/data -web /opt/mengka-ob/web/dist
```

缺少前端入口时程序会报错退出，避免显示空白页面或在错误位置创建管理员。不要只拷贝可执行文件，需保留整个 `web/dist`。

## Linux 后台与开机启动

将完整安装目录放在 `/opt/mengka-ob`，创建专用运行用户并让它拥有该目录（在线升级需要写入程序和前端目录）：

```sh
sudo useradd --system --home-dir /opt/mengka-ob --shell /usr/sbin/nologin mengka-ob
sudo chown -R mengka-ob:mengka-ob /opt/mengka-ob
```

保存 `/etc/systemd/system/mengka-ob.service`：

```ini
[Unit]
Description=Mengka OB
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=mengka-ob
Group=mengka-ob
WorkingDirectory=/opt/mengka-ob
ExecStart=/opt/mengka-ob/mengka-ob
Restart=on-failure
RestartSec=3
TimeoutStopSec=30
UMask=0077

[Install]
WantedBy=multi-user.target
```

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now mengka-ob
sudo systemctl status mengka-ob --no-pager
sudo journalctl -u mengka-ob -n 50 --no-pager
```

这个示例没有写死 `-listen`，初始化保存的端口在重启后可生效。需要限制本机访问时，可在 `[Service]` 添加 `Environment=MENGKA_OB_LISTEN_HOST=127.0.0.1`。

## 外网访问排查

先在服务器执行：

```sh
ss -lntp | grep ':18080'
curl --noproxy '*' http://127.0.0.1:18080/healthz
```

- 没有监听：检查日志、目录权限、前端文件是否完整和端口是否被其他服务占用。
- 显示 `127.0.0.1:18080`：检查旧程序、`-listen` 参数及监听环境变量。该地址只允许服务器自身访问。
- 显示 `*:18080`、`0.0.0.0:18080` 或 `[::]:18080` 且本机健康检查正常：从另一台设备访问公网 IP；若超时，再检查云安全组、系统防火墙与 NAT 端口映射。
- 修改端口后需同步调整云安全组、防火墙、反向代理和访问 URL。不要把服务器的 NAT 公网 IP 直接设为本地监听网卡。

### 域名反向代理

反向代理必须保留浏览器访问的域名，不能把 `Host` 设置为 `localhost` 或上游 IP；否则登录续期与 WebSocket 会被同源校验拒绝，可能反复进入服务恢复页。宝塔反向代理的“发送域名”请使用原域名，或在 Nginx 中使用 `$http_host`（同时保留访问端口）。

```nginx
location / {
    proxy_pass http://127.0.0.1:18080;
    proxy_http_version 1.1;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_buffering off;
    proxy_read_timeout 600s;
}
```

聊天实时通知使用 SSE，代理需要关闭响应缓冲；账号状态和插件 WebSocket 需要转发 Upgrade。修改配置后先执行 `nginx -t` 再重载。保持后端跨站校验开启，无需放开任意 Origin。

直接 HTTP 管理页与官方 Webhook 回调是两回事：管理页可用 IP＋端口访问；Webhook 回调仍需开放平台要求的公网 HTTPS 地址。

## 官方机器人与升级

添加 AppID、AppSecret、接入方式与名称，保存后默认停用。WebSocket 主动连接 QQ 网关；Webhook 使用账号页生成的 `/webhooks/official/{AppID}` 回调地址，配置 HTTPS 后在开放平台验证。仅部分账号需要设置出站 IP 白名单，框架探测的出站 IP 不替代 HTTPS 回调域名。

管理员密码使用 bcrypt 保存。备份整个 `data` 目录，尤其数据库与 `master.key`；密钥丢失将无法解密 Bot 凭据。不要让多个进程共用同一数据目录，也不要使用 NT 的数据目录。

计划内重启可保留未过期的管理会话，自动登录只恢复原有已启用的 Bot。在线更新、一键重启和独立 OB 最低版本策略见 [更新与重启](runtime-update.md)、[算法接入](algorithm-integration.md)。
