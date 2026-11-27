<div align="center">
  <img src="mengka-logo.png" width="256" alt="萌卡 OB" />

  <p>
    <a href="https://github.com/Carlor-Official/Mengka-OB/releases/latest"><img src="https://img.shields.io/badge/下载-GitHub%20Releases-7C5CFC?style=flat-square" alt="GitHub Releases" /></a>
    <img src="https://img.shields.io/badge/平台-Windows%20%7C%20Linux-2684FF?style=flat-square" alt="Windows 与 Linux" />
    <img src="https://img.shields.io/badge/架构-AMD64%20%7C%20ARM64-7C5CFC?style=flat-square" alt="AMD64 与 ARM64" />
    <img src="https://img.shields.io/badge/管理-WebUI-F59E0B?style=flat-square" alt="WebUI 管理" />
    <img src="https://img.shields.io/badge/插件-IPC%20%7C%20WebSocket-00ADD8?style=flat-square" alt="插件接入" />
  </p>

  <p><strong>萌卡 OB</strong></p>
  <p>Mengka OB</p>
  <p>面向 QQ 官方机器人的跨平台自托管框架</p>
  <p>多机器人管理 · 可视化 WebUI · 插件扩展 · Windows / Linux</p>

  <p>
    <a href="https://github.com/Carlor-Official/Mengka-OB/releases/latest">下载最新版</a>
    · <a href="https://mengka.net/ob/">项目官网</a>
    · <a href="https://mengka.net/ob/deployment.html">部署指南</a>
    · <a href="https://mengka.net/ob/api/">API 文档</a>
    · <a href="https://github.com/Carlor-Official/Mengka-OB/issues">问题反馈</a>
  </p>
</div>

---

## 项目简介

萌卡 OB（Mengka OB）是一套面向 QQ 官方机器人的框架，将机器人账号、消息会话、插件服务和运行状态集中到浏览器中管理。

框架支持 Windows 与 Linux，可通过手机 QQ 扫码授权添加机器人，也可手动填写 QQ 开放平台的 AppID 和 AppSecret。一个部署可管理多个机器人，每个机器人独立选择 WebSocket 或 Webhook 接收官方事件。

首次启动直接初始化自己的管理员账号，**无需注册卡或验证端账号**。版本服务仅用于 OB 的版本检查。

本仓库用于发布安装包、公开使用资料和接收问题反馈，框架前后端源码分别维护在私有仓库中。完整部署与开发文档请访问[官网](https://mengka.net/ob/)。

## 核心能力

| 模块 | 能力 |
| --- | --- |
| 机器人管理 | 扫码或手动添加多个官方机器人，分别管理接入方式、事件接收范围、启停与运行日志 |
| 官方事件接入 | WebSocket 主动连接官方网关，或通过 Webhook 接收并校验 HTTPS 回调 |
| 消息与聊天 | 查看实时会话，发送文字、图片、Markdown、按钮和官方消息模板，查看引用与发送结果 |
| 会话与记录 | 按机器人查看消息日志，管理实际事件中出现的群组、用户、备注和标签 |
| 官方接口 | 调用官方消息、群管理、频道、菜单、面板及交互接口，查看官方返回内容 |
| 插件扩展 | 导入本机 IPC 插件，或通过正向、反向 WebSocket 接入外部服务 |
| 插件管理 | 选择授权机器人、接口与事件，管理插件配置、运行状态和日志 |
| 可视化管理 | 浏览器管理后台、移动端适配、主题设置、消息预览与在线接口调试 |
| 运行维护 | 版本检查、在线更新、框架重启、站点设置与邮件通知 |

接口调用结果以 QQ 官方返回为准。群组与用户列表来自实际事件，并非完整 QQ 通讯录。完整调用方式见 [API 文档](https://mengka.net/ob/api/)。

## 平台支持

| 平台 | 安装包 | 启动文件 | 架构 |
| --- | --- | --- | --- |
| Windows | ZIP | `mengka-ob.exe` | AMD64 / x86_64 |
| Linux | TAR.GZ | `mengka-ob` | AMD64 / x86_64 |
| Linux | TAR.GZ | `mengka-ob` | ARM64 / aarch64 |

## 快速开始

### 1. 下载与解压

从 [GitHub Releases](https://github.com/Carlor-Official/Mengka-OB/releases/latest) 下载对应系统的安装包和 `SHA256SUMS.txt`，核对校验值后完整解压到独立目录。

保留程序及配套的 `web/dist` 目录，不要只复制可执行文件。

### 2. 启动框架

<details open>
<summary><strong>Windows</strong></summary>

在解压目录运行：

```powershell
.\mengka-ob.exe
```

</details>

<details>
<summary><strong>Linux</strong></summary>

在解压目录执行：

```bash
chmod +x ./mengka-ob
./mengka-ob
```

后台常驻、开机启动和域名反向代理配置见[部署指南](https://mengka.net/ob/deployment.html)。

</details>

### 3. 完成初始化

1. 本机默认访问 `http://127.0.0.1:18080`；远程部署使用服务器地址和实际监听端口。
2. 按页面阅读并确认协议，设置自己的管理员账号和密码，无需填写注册卡。
3. 完成初始化后，使用管理员账号登录控制台。

若修改了监听地址或端口，以实际启动配置为准。远程访问还需检查服务器安全组、防火墙与反向代理配置。

### 4. 添加 QQ 官方机器人

在 OB 账号列表点击添加机器人，选择“扫码添加”，使用手机 QQ 扫码并选择要授权的机器人。授权后核对 AppID、填写名称并保存；也可选择“手动填写”，使用 [QQ 开放平台](https://q.qq.com/)提供的 AppID 与 AppSecret。每个机器人可选择以下接入方式：

| 接入方式 | 配置方式 |
| --- | --- |
| WebSocket | 由框架主动连接 QQ 官方网关，配置事件接收范围后启用机器人 |
| Webhook | 准备公网 HTTPS 地址，将账号页面提供的回调地址填写到 QQ 开放平台并完成验证 |

保存后启用机器人，在已开通的会话中发送一条消息，通过账号事件日志确认真实收件。需要自动回复或推送业务时，再安装对应插件并授权该机器人。

如果 QQ 开放平台已设置 IP 白名单，需要包含部署服务器实际使用的公网出口 IP；扫码授权不会自动修改白名单。

完整流程见[快速开始](https://mengka.net/ob/guide/getting-started.html)。

## WebUI

- **概览**：查看框架运行状态、机器人和消息统计。
- **账号列表**：管理机器人凭据、接入方式、连接状态与事件日志。
- **聊天与消息**：浏览会话、发送消息，编辑 Markdown、按钮和消息模板。
- **群组与用户**：查询已发现的会话对象，维护本地备注与标签。
- **插件服务**：导入插件包，配置外部服务、授权范围和插件设置。
- **接口调试**：填写字段、预览请求，查看接口返回与错误信息。
- **框架配置**：管理站点、邮件通知、运行设置与版本更新。

## 插件开发

萌卡 OB 使用 `obp/1` 协议。本机插件通过 IPC 由框架托管运行；独立部署的插件服务可通过正向或反向 WebSocket 连接。

插件按 AppID 区分机器人，在清单与服务配置中声明所需接口和事件，并使用框架提供的插件数据目录保存持久状态。

接入说明：[开发总览](https://mengka.net/ob/development/) · [开发入门](https://mengka.net/ob/development/getting-started.html) · [连接与握手](https://mengka.net/ob/reference/connections.html) · [插件包清单](https://mengka.net/ob/development/packaging.html)

### Python SDK

Python SDK 面向本机 IPC 插件，封装握手、心跳、机器人上下文、事件处理与接口回执，附带最小回复示例。

[SDK 源码](sdk/python/) · [Python 回复示例](sdk/python/examples/echo/) · [构建与验证](sdk/python/README.md#构建与验证)

下载 [SDK 与示例 ZIP](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip) 和 [SHA256 校验文件](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip.sha256)。安装、调用方式和异常处理见 [Python SDK 文档](https://mengka.net/ob/development/python-sdk.html)。该下载对应框架 1.0.4 的 SDK 快照。

需要 Python 3.10 或更高版本，依赖见归档中的 `requirements.txt`。请按[打包说明](https://mengka.net/ob/development/packaging.html)准备插件入口、清单与运行环境；更新框架不会自动替换已安装插件中的 SDK。

其他语言可参考 [Go IPC 示例](examples/ipc-echo/)及[协议参考](https://mengka.net/ob/plugin-protocol.html)。NT SDK 与 OB 的连接协议不同，已有 NT、OneBot 或其他框架插件需适配后接入。

## 数据与更新

- 默认运行数据保存在安装目录的 `data` 中；使用自定义数据路径时，以实际配置为准。
- 更新前备份当前数据、插件目录及密钥，尤其是 `master.key`，它用于解密机器人凭据。
- 在线更新按控制台提示执行；手动更新前停止框架，配套替换程序与 `web/dist`，保留现有配置、插件和数据。
- 1.0.4 使用新的存储格式，不能直接降级到 1.0.3 或更早版本。升级与回退说明见[下载与升级](https://mengka.net/ob/releases/)。
- 发行包不包含预设管理员、机器人配置、业务插件包或用户运行数据。

## 常见问题

<details>
<summary><strong>管理页面无法打开或显示空白</strong></summary>

确认框架已启动，使用正确的地址和端口，并检查 `web/dist` 是否完整。远程部署检查安全组、防火墙和反向代理；代理需保留访问域名、支持 WebSocket，并关闭实时消息的响应缓冲。具体配置见[部署指南](https://mengka.net/ob/deployment.html)。

</details>

<details>
<summary><strong>Webhook 显示“等待回调”，或没有收到消息</strong></summary>

“等待回调”不等于连接失败。检查开放平台中的 HTTPS 回调地址、验证结果与事件接收范围，确认机器人已启用，再在可用会话中发送消息并查看事件日志。完整回调路径使用账号页面提供的地址。

</details>

<details>
<summary><strong>消息发送失败或结果未确认</strong></summary>

查看发送记录中的官方返回内容与错误码，按实际原因处理。明确失败和结果未知不同；超时不代表消息一定没有发送，不要直接重复投递。“已发送”表示接口接受，不代表对方已读。开发者可查阅[错误与重试](https://mengka.net/ob/reference/errors.html)。

</details>

<details>
<summary><strong>插件无法连接或没有响应</strong></summary>

检查插件运行状态、连接方式、地址、令牌和机器人授权，并确认已声明需要的接口与事件。本机 IPC 插件还需检查入口文件、系统架构和运行依赖。排查步骤见[开发排错](https://mengka.net/ob/development/troubleshooting.html)。

</details>

## 下载与反馈

- 安装包与更新记录：[GitHub Releases](https://github.com/Carlor-Official/Mengka-OB/releases/latest)
- Python SDK：[源码与示例](sdk/python/) · [下载 ZIP](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip) · [接入文档](https://mengka.net/ob/development/python-sdk.html)
- 使用与开发：[使用指南](https://mengka.net/ob/guide/) · [开发文档](https://mengka.net/ob/development/) · [API 参考](https://mengka.net/ob/api/) · [事件参考](https://mengka.net/ob/events/)
- Bug 与建议：[提交 Issue](https://github.com/Carlor-Official/Mengka-OB/issues)

反馈时请提供版本、操作步骤和脱敏后的错误信息，不要提交 AppSecret、管理员密码、访问令牌、私有消息或数据库文件。
