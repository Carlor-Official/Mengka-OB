# Python IPC 回复示例

收到单聊 `ping`，或群里 @ 机器人的 `ping` 后回复 `pong`。只申请 `send_message` 和对应两类消息事件。

本目录仅包含示例代码和清单，运行时还需同级 `obp/` 与依赖。推荐下载[完整 SDK 示例包](https://github.com/Carlor-Official/Mengka-OB/raw/refs/heads/main/sdk/releases/mengka-ob-python-sdk.zip)，或在仓库根目录运行：

```bash
python sdk/python/scripts/build_release.py
```

得到的 `sdk/releases/mengka-ob-python-sdk.zip` 将本目录的 `main.py`、`echo_plugin.py` 和 `mengka.plugin.json` 放在根目录，并带上 SDK 与 `requirements.txt`。

在框架使用的 Python 环境安装依赖后导入该 ZIP，选择机器人并授权。框架提供 IPC 环境、服务令牌和持久数据目录；无需在源码或清单中填写 AppID、AppSecret 或服务令牌。

开发自己的插件时修改插件 ID、名称、版本及处理器，再按实际功能声明权限。示例仅说明回复链路，不是包含业务重试、订阅或支付通知逻辑的推送插件。

[SDK 说明](../../README.md) · [官网入门](https://mengka.net/ob/development/getting-started.html)
