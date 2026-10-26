# Mac 整机克隆后 Codex 远程连接异常：重复设备身份排查与恢复

[English](README.md) · [多语言入口](README.md#codex-remote-connection-recovery-after-mac-cloning)

适用于“从另一台 Mac 整机克隆/迁移后，两台 Codex 无法正常远程连接”，尤其日志出现 **`409 Conflict: Remote app server already online`** 的情况。保留原电脑，在克隆机上让应用正常生成新安装身份并重新注册主机。

本项目是独立排查记录和工具，不是 OpenAI 官方修复程序。写操作仅支持已分析的 macOS 桌面版本 **26.1021.31345，build 21828**；其他版本需要重新核对实现。

## 已确认的案例

两台机器的安装 ID、`~/.codex/installation_id`、环境 ID、SQLite `server_id` 完全相同；控制端 `clientId`、`keyId` 不同。同账号的 `accountUserId`、`account_id` 相同属于正常现象。日志存在同一主机注册的 already online 409，证明存在重复注册问题，但不能证明这是唯一故障原因。

## 不要只清 JSON

- `~/.codex/installation_id` 是 CLI 共用的持久安装标识，不能只改桌面缓存。
- `electron-local-remote-control-installation-id`、`electron-local-remote-control-environment-id` 会随 app-server 状态通知重新写回。
- `state_5.sqlite` 的 `remote_control_enrollments` 保存服务端主机注册，需要只处理准确匹配的单条记录。
- `electron-remote-control-client-enrollments` 是另一套控制端授权；本案例密钥不同且曾成功注册，脚本保留这些记录。

安装 ID 也用于 CLI 的其他安装关联，重建它并非严格意义上的“仅改远程专用字段”。脚本不更改系统 UUID、会话、项目、模型设置、自动化 ID 或账号凭据，不撤销原电脑的服务端注册。

## 使用步骤

仅在克隆机运行，需要 macOS、Python 3.9+，无需第三方依赖。先在两台电脑只读对比身份，再在克隆机执行：

```sh
python3 codex_clone_identity.py --plan-out clone-plan.local.json
```

默认只读，除指定的本地计划文件外不改配置。计划包含账号和设备标识、路径，不要上传。自定义目录可用 `--home /absolute/path/to/.codex`，也支持 `CODEX_HOME`。多账号用 `--account-id ACCOUNT_ID` 选择，状态不一致或选择不唯一时停止。

核对计划后，在应用之外的终端执行：

```sh
python3 codex_clone_identity.py --plan clone-plan.local.json --apply --wait-for-exit
```

完全退出 Codex，包括所有 Codex CLI/app-server；关闭窗口不等于退出。程序等待最多 30 分钟，检测到相关进程退出约 10 秒后才执行；不会主动结束进程。Ctrl+C 可取消。重置期间不要重新打开应用。

脚本退出后再次备份，以 SQLite 事务删除匹配的单条主机注册，移除 JSON 及 `.bak` 的两个缓存字段，移走安装 ID 文件，让程序重新生成。保留所有控制端 enrollment 和密钥。完成后重新打开应用，在设置页启用远程连接，由服务端返回新 environment/server ID。

## 验证与限制

案例中本地重置实际成功，重启后已观察到新 installation/environment ID。尚未独立验证两台机器同时在线并分别成功连接，因此不能宣称全面修复。

工具验证其他数据库表、其他主机行和 JSON 非目标值保持不变；已测试模拟写入失败时回滚。断电/强制终止时，多个文件与数据库无法跨资源原子提交；备份必须保留，发生异常先检查现状，不要盲目重复运行。进程检查不能阻止其他进程恰好重新启动，操作时应保证所有写入者停止。

`recovery-local/` 含配置、登录文件和聊天数据库备份，属于私人数据，不能提交 GitHub。失败时退出所有相关程序，结合退出后备份按目标字段/文件/记录恢复；整库恢复可能覆盖新工作。恢复旧安装身份会重新引入克隆冲突。

[完整英文操作与限制](README.md) · [匿名案例与证据](docs/CASE-STUDY.md)

检索词：Codex 远程连接失败、整机克隆、迁移助理、Mac 换机、设备身份重复、远程设备注册冲突、两台电脑互相看不到、installation_id 重复、environment_id 重复、server_id 重复、Remote app server already online、HTTP 409。
