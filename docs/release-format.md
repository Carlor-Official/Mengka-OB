# GitHub 发布格式

萌卡 OB 的 GitHub Release 沿用萌卡 NT 的命名与正文结构。

## 标题与版本

- 发布标题：`萌卡 OB v1.0.4-beta`。
- 正文一级标题与发布标题一致：`# 萌卡 OB v1.0.4-beta`。
- Git 标签保留 `v` 前缀，例如 `v1.0.4-beta`；程序内部版本与文件名使用 `1.0.4-beta`。
- `-beta`、`-beta.1` 属于版本号，不改写为其他形式；内测版本保留 GitHub 的 Pre-release 标记。

## 正文结构

依次使用有实际内容的“新增／调整／修复／优化／升级说明”二级标题，无内容的分区省略。变化使用简明列表，升级说明使用短段落。保留对应版本的升级条件、行为变化与必要限制，不把新版能力回填进旧版说明。

## 安装包与校验文件

与 NT 一样使用小写产品名、版本、系统、架构和对应后缀：

```text
mengka-ob-1.0.4-beta-windows-amd64.zip
mengka-ob-1.0.4-beta-linux-amd64.tar.gz
mengka-ob-1.0.4-beta-linux-arm64.tar.gz
SHA256SUMS.txt
```

在线更新器按上述名称查找文件。整理历史发布说明时，保留现有标签、发布时间、内测标记、附件名称、下载地址与校验值，不重新打包或替换已发布附件。

发布正文与本仓库 `docs/releases/<version>.md` 同步维护。
