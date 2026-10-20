# Markdown 发送与 Windows QQ 样式对照

聊天工具栏的“发送格式”可选择文字、Markdown、图片及模板。Markdown 模式使用左右分屏编辑与实时预览，窄屏改为上下排列。Enter 换行，Ctrl+Enter 或“发送 Markdown”提交；输入法组词期间不会提交。发送成功后清空正文并保留 Markdown 模式；切换账号或会话会重置草稿。

预览和聊天消息使用同一 `ChatMarkdown` 渲染器，发送使用官方 `msg_type=2` 与未经展示加工的 `markdown.content`。预览更新不会调用发送接口；预览的链接与图片沿用消息展示的安全处理。

Markdown 的局部消息样式按 Windows QQ 对齐：正文 14px / 22px，二级标题 18px / 27px，行内代码 11px，段落间距 12px，引用使用灰色边线、链接使用 QQ 蓝色。明亮和黑暗主题分别使用中性色卡片，不继承框架的粉色强调色。外围仍保留 NT v2.6.0 控件样式。

QQ 的双下划线加粗及图片尺寸标记参考[官方 Markdown 说明](https://bot.q.qq.com/wiki/develop/api-v2/server-inter/message/type/markdown.html)。Markdown 图片保留指定宽高比例，长图不再套用普通聊天缩略图的 256px 高度上限；过宽图片在消息可用宽度内等比例显示。QQ 专属 `mqqapi://aio/inlinecmd` 链接展示指令文字，不在 OB 冒充 QQ 用户执行。

验收使用 Windows QQ 已存在的同一条机器人消息，没有发送真实 QQ 测试消息。当前样本原生卡片约 295×275px，OB 为 295.4×275px；这不代表不同 QQ 版本、字体、缩放或所有消息都逐像素一致。还验证了 390px 上下分屏、两种主题、动态修改预览、回车不误发、Ctrl+Enter 发送、发送正文完整保留，以及预览和发送后 HTML 一致。

此功能已整合到 1.0.3beta 完整安装包。原有 1.0.2beta 用户可通过在线更新升级，更新后强制刷新浏览器。
