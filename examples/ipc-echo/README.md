# IPC 示例插件

本示例使用标准库实现新的 obp/1 协议，不依赖 NT、OneBot 或旧官机云 SDK。

编译所需平台：Windows 用 `go build -o echo.exe main.go`，Linux 用 `go build -o echo main.go`。ZIP 根目录放 `mengka.plugin.json` 和两个入口文件；只发布一个平台时，从清单中删除另一平台入口。

在“插件导入”上传后，选择“创建服务”，授予所需 Bot、`send_message` 和对应消息事件，再确认信任并启动。向已授权 Bot 发送 `/ob ping` 会触发真实回复。

stdout 仅传输 JSON 协议，stderr 输出日志；接口调用 ID 由事件 ID 派生，重投事件不会使用新的发送 ID。
