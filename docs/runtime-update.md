# 萌卡OB 更新与重启（0.9.0-dev）

## 使用方式

算法后台按 `framework_type=ob` 管理萌卡OB最低版本和重启指令，与 NT 独立。框架启动后声明 `restart` 能力；收到有效签名指令后先持久化编号，再重启。新进程初始化完成后回执，重复指令不会重复执行。

框架设置提供“一键重启”和“自动更新”。普通自动更新默认关闭，开启后每 10 分钟检查正式发行版本。低于有效签名策略中的 OB 最低版本时，无论普通自动更新是否开启，均自动执行更新。管理员无需保持网页打开；业务接口在版本满足要求前受限，账号启停配置不变。

进度、失败重试和完成弹窗复用当前 NT `ForcedUpdateNotice.vue` 的布局与按钮。关闭弹窗不中断更新。计划内重启会加密保存未过期的本地管理会话；凭据改变后不会恢复旧会话。

## 发行包

仅读取 `Carlor-Official/Mengka-OB` 的 GitHub 正式发行版，按当前 OS/架构选择唯一文件：

- `mengka-ob-<version>-windows-amd64.zip`
- `mengka-ob-<version>-linux-amd64.tar.gz`
- `mengka-ob-<version>-linux-arm64.tar.gz`

必须提供 GitHub asset 的 `digest=sha256:<hex>` 和正确大小。下载会测试直连及内置镜像线路并自动尝试备用线路，所有来源均用官方元数据中的同一 SHA-256 校验。包内必须包含 `mengka-ob-release.json`、对应可执行文件和 `web/dist`。拒绝路径穿越、链接、重复路径、额外数据目录、错误平台/版本以及不满足最低版本的发行包。安装前执行新程序 `-version` 验证产品、版本和架构。

构建完成后生成发行包：

```sh
python scripts/package-release.py --binary bin/mengka-ob.exe --web web/dist --output artifacts
```

交叉编译时可传入 `--version`、`--goos`、`--goarch`；下载客户端仍会验证实际二进制。发行版本应是正式三段版本号。没有正式发行包、缺少对应平台或校验失败时会明确报错并保留现有版本，不会假报成功。运维应先发布完整发行包，再提高最低版本。本次开发部署不自动发布 GitHub 正式版本或修改生产门槛。

## 安装与恢复

只替换正在运行的可执行文件和配置的前端目录，不合并或覆盖私有数据目录。两者分别保留带 `.backup-<id>` 后缀的旧副本；文件替换或新进程交接失败时回退。仅新进程就绪且版本达到目标与门槛后标记完成。Linux 使用 exec 保留服务主 PID；Windows 子进程持有父进程句柄，等待父进程释放数据库和 Bot 连接后启动。

进程崩溃、断电或新版本启动后发生故障仍可能需要运维恢复备份；不要在未验证新版本运行前清理备份。容器/只读部署无法写入安装位置时会返回失败，应更新镜像或按原部署方式升级。

管理接口均沿用身份验证与同源检查：

- `GET /api/v1/system/runtime`：进程标识、更新阶段和结果。
- `POST /api/v1/system/restart`：本机重启。
- `GET /api/v1/system/update`：读取对应平台发行信息。
- `POST /api/v1/system/update/apply`：安装最新正式版本。
- `POST /api/v1/system/update/retry`：携带当前失败任务 `id`，避免重复/过期重试。

## 验证

`node scripts/verify-runtime-update.mjs` 使用隔离签名服务、安装目录、管理员和发行包，验证关闭普通自动更新时的强制更新、坏校验码拒绝、真实程序/前端替换、NT 弹窗重试与完成、数据与会话保留，以及签名重启一次执行和启动后回执。该测试不会登记生产账号或调整生产策略。
