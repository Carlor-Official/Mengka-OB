# 萌卡 OB 版本检查

萌卡 OB 可直接部署并初始化本地管理员，无需注册卡、验证端账号、设备登记或会话续期。本地管理员凭据、机器人配置、插件和消息数据保存在 OB 实例内。

## NT 与 OB 分开管理

验证端的“版本管理”提供“萌卡 NT”和“萌卡 OB”切换，分别保存公开发布来源、版本启停和最低版本要求。OB 默认发布源为 `https://github.com/Carlor-Official/Mengka-OB`。NT 的原有注册、授权和算法服务使用自己的版本目录，OB 设置不会触发 NT 会话停用。

OB 仅通过 HTTPS 查询 `GET /versions/check?framework=ob&version=<当前版本>`。默认验证端为 `https://qqsign.bilibilibot.com`，可通过 `MENGKA_OB_VERIFIER_URL` 指定 HTTPS 源地址。请求不包含注册卡、令牌、设备码、程序指纹、管理员密码校验值或业务数据。旧的 `/ob-access` 注册适配服务已退役。

已明确停用的 OB 版本或低于 OB 最低版本时暂停业务执行，保留本地管理员登录和原有账号启停设置。未知但格式有效、满足最低版本的部署版本可直接使用，不要求管理员逐个批准程序指纹。版本限制恢复后恢复原先启用的机器人。

版本服务暂时不可用时沿用最后一次有效的 OB 版本策略，不因网络故障使现有实例突然失去“授权”；全新实例没有缓存策略时可继续初始化。已有停用限制不会因断网或重启被清除。策略按验证端地址和当前版本绑定保存，每 60 秒重新检查。首次同步失败后每 15 秒重试。

## 升级

先部署验证端的双产品版本目录及 `/versions/check`，再更新 OB 核心和前端。原 `MENGKA_OB_VERIFIER_URL=https://qqsign.bilibilibot.com/ob-access` 配置应改为源地址 `https://qqsign.bilibilibot.com`，不再配置 `MENGKA_OB_REGISTRATION_FILE`。

历史加密安装身份和旧会话设置仅保留以供回退，不再读取或上传；不需要删除现有数据库。更新时保留当前数据、机器人配置、插件权限和收据。公开发行包不得包含生产数据或业务插件。

低于最低版本时仍通过原有 OB 更新机制检查对应通道的发行包，校验后更新；详见 [更新与重启](runtime-update.md)。版本检查不提供远程重启或注册授权能力。

## 管理接口

- `GET /api/v1/system/framework-access`：读取 OB 版本状态，`mode=version_only`，没有授权租期。
- `POST /api/v1/system/framework-access/refresh`：主动检查 OB 版本，保留现有管理会话和同源校验。
- `GET /api/v1/open/framework-version-policy`：更新页读取当前 OB 版本策略。

验证端的 NT 原接口默认仍为 NT；`GET /versions?framework=ob` 查询 OB 可用版本。公开 OB 版本检查不会签发 NT 账号、注册卡、会话或算法权限。
