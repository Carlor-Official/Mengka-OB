# 萌卡 OB Python SDK

用于萌卡 OB 本机 IPC 插件的 Python SDK，封装 `obp/1` 握手、心跳、机器人上下文、事件处理和接口回执。需要 Python 3.10 或更高版本。

[下载 SDK 与回复示例 ZIP](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip) · [SHA256 校验](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip.sha256) · [源码](https://github.com/Carlor-Official/Mengka-OB/tree/main/sdk/python) · [官网文档](https://mengka.net/ob/development/python-sdk.html)

当前源码对应框架 **1.0.4** 的通用 SDK 快照，来源和模块校验值记录在 `contract-source.json`。框架版本、插件版本和协议版本分别管理；这里不是 PyPI 软件包，也不包含 Python 运行时。

## 目录结构

仓库中的源码与示例分开维护：

```text
sdk/
├── python/
│   ├── obp/                    # SDK 源码
│   ├── examples/echo/          # 最小回复示例与插件清单
│   ├── requirements.txt       # 运行依赖
│   ├── contract-source.json   # 来源与模块校验值
│   ├── scripts/build_release.py
│   └── tests/                 # 发行包与 IPC 回归
└── releases/
    ├── mengka-ob-python-sdk.zip
    └── mengka-ob-python-sdk.zip.sha256
```

下载包将回复示例放在 ZIP 根目录，解压后即可按下面的流程准备插件：

```text
main.py
echo_plugin.py
mengka.plugin.json
requirements.txt
README.md
contract-source.json
obp/
```

## 安装与运行示例

1. 下载 ZIP 和校验文件，核对 SHA256 后解压。
2. 在框架实际使用的 Python 环境安装依赖：

   ```bash
   python -m pip install -r requirements.txt
   ```

3. 在 OB 的插件导入页面导入 SDK 示例 ZIP，创建插件服务并选择自己的机器人。
4. 授予示例清单中的 `send_message`、`C2C_MESSAGE_CREATE` 和 `GROUP_AT_MESSAGE_CREATE`，确认可信来源后启动。
5. 在单聊发送 `ping`，或在群中 @ 机器人发送 `ping`，示例回复 `pong`。

框架不会在导入时自动安装依赖；使用虚拟环境时，确认框架的 Python 启动器使用该环境。不要直接执行 `main.py` 来代替框架启动，IPC 环境、令牌和数据目录由框架提供。

从 GitHub 克隆源码时，在仓库根目录运行 `python sdk/python/scripts/build_release.py` 即可生成同样布局的 ZIP。详细部署步骤见[开发入门](https://mengka.net/ob/development/getting-started.html)。

## 编写事件处理器

```python
from obp.module import Module, on_event

class EchoPlugin(Module):
    @on_event("C2C_MESSAGE_CREATE", "GROUP_AT_MESSAGE_CREATE")
    async def echo(self, context, message):
        if message.content.strip() != "ping":
            return 0
        result = await context.reply(message, "pong")
        if isinstance(result, dict) and result.get("code"):
            raise RuntimeError(f"QQ 拒绝回复，业务码：{result['code']}")
        return 1
```

入口 `main.py`：

```python
from obp.runtime import run
run("echo_plugin")
```

`return 1` 表示消费当前事件，`return 0` 表示不消费。框架服务的 handler/broadcast 模式决定是否影响后续服务。`message.raw` 保留原始官方事件；AppID、OpenID、消息 ID 按字符串处理。

完整示例：[examples/echo](https://github.com/Carlor-Official/Mengka-OB/tree/main/sdk/python/examples/echo)。

## 调用接口

```python
profile = await context.api.get_user_info("USER_OPENID")
group = await context.api.call("get_group_info", target="GROUP_OPENID")
await context.reply(message, "收到消息")
```

`context.api` 自动绑定当前机器人的 AppID，不能传入 `app_id` 覆盖。调用额外接口前，在插件清单和服务配置中声明并授权对应 action。接口参数、消息格式和返回字段见 [API 参考](https://mengka.net/ob/api/)。

## 返回与错误

高层 `context.api` 遇到带官方业务码的明确拒绝时，可能返回官方错误对象；协程正常返回不代表消息发送成功，应检查业务码和预期成功字段。

低层 `obp.runtime.peer().call()` 失败时抛出 `RPCError`，其中 `official_response` 保留可用的官方响应。`RPCError.uncertain` 表示已识别的未知结果；断线、取消及普通超时也不能据此认定未发送。

SDK 不自动重放未知发送。事件完成记录不能替代业务事务，业务推送仍需持久保存去重标识和提交状态。详见[错误与重试](https://mengka.net/ob/reference/errors.html)及[事件投递](https://mengka.net/ob/events/delivery.html)。

## 配置与数据

通过 `obp.state.read_settings()`、`mutate_settings()` 和 `data_path()` 管理模块设置与数据。持久目录由 `OB_PLUGIN_DATA_DIR` 指定，不向安装包目录写入运行数据；备份时同时保留数据和对应密钥。

stdout 专用于 IPC 协议，日志使用 Python logging 输出到 stderr。更新框架不会自动替换已有插件内的 SDK，升级插件时应保留框架分配的数据目录。

## 构建与验证

在仓库根目录执行：

```bash
python -m pip install -r sdk/python/requirements.txt
python sdk/python/scripts/build_release.py
python sdk/python/scripts/build_release.py --check
python -m unittest discover -s sdk/python/tests -v
```

打包脚本只包含明确列出的 SDK、回复示例、依赖说明和来源文件；固定归档顺序与时间戳，可重复构建。`--check` 检查当前源码、ZIP 和 SHA256 是否一致，不改写文件。测试使用临时数据目录与模拟框架，不连接 QQ、不发送真实消息。

本 SDK 仅实现本机 IPC，NT Node.js SDK 与 OB 协议不兼容。需要独立 WebSocket 客户端时，按[连接与握手](https://mengka.net/ob/reference/connections.html)实现。
