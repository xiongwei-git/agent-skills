# 首次接入

安装 Skill 后第一次查询，先检查普通工具是否可用。可用则直接使用；缺失时说明“需要一次普通访问授权，我会引导完成配置”。不要要求用户研究 MCP。

## 准备

本机测试地址已预置为 `http://127.0.0.1:18765/mcp`，在运行服务的同一台机器上只需普通 API Key，不再要求用户配置地址。远程用户才需要管理员提供普通 HTTPS `/mcp` 地址。目前没有公开申请渠道，提示“请向邀请你的管理员申请普通 API Key 和接入地址”。不编造联系人。管理员 Key 不可代替普通 Key。

脚本仅使用 Python 3 标准库；Codex 配置还需要已有 codex CLI。查看 `python3 scripts/connect.py --help`。路径按已安装 Skill 目录展开，命令中的 SERVICE_URL 由实际服务地址替换。如果没有 Python/Codex CLI，说明缺少的运行条件，使用客户端原生配置界面，不擅自安装依赖。

## Codex

用户明确要求配置连接后，先运行脚本的 check。没有配置时让用户在本机交互终端执行：

```bash
python3 /实际安装目录/cinevault-query/scripts/connect.py setup
```

本机测试直接执行上述命令；远程接入在命令末尾追加 `--url SERVICE_URL`。脚本提示隐藏输入普通 API Key，先在线校验普通工具，再保存配置并注册 MCP。不要通过聊天、命令参数、环境打印或脚本源文件传入 Key。用户已有权限600的私密 Key 文件时，可追加 `--key-file /私密文件路径`，该文件仅包含 Key；由脚本读取，模型不读取文件内容。不要拿开发项目 .env 自动替代用户授权。

脚本将 URL 与 Key 存于 `~/.config/cinevault/reader.json`（600），并注册 `cinevault-query` 本机 STDIO 桥接。配置不在 Skill 目录中，更新 Skill 不覆盖凭据。远程必须 HTTPS；仅本机环回允许 HTTP。重定向拒绝，避免泄露认证。脚本面向 CineVault 的 JSON HTTP 响应及有限 SSE 响应，不作为通用 MCP 代理。

配置已有：运行 `python3 /实际安装目录/cinevault-query/scripts/connect.py check`。连接注册失败但配置已保存：运行 register，仅在该连接名称尚不存在时重试。不得直接读回或展示 reader.json。需要更新凭据时先按用户明确范围备份已有私密配置并处理现有连接；脚本拒绝直接覆盖。

通过后尝试重新发现工具；仍无工具时提示新开聊天，例如：`$cinevault-query 继续查询洛杉矶劫案，使用已配置的普通连接。` 工具校验只证明连接与角色通过，不证明电影已收录。

## 其他客户端

提供服务地址、普通端点路径 /mcp 与 Bearer 认证要求。用户通过客户端秘密存储填写 API Key；不将 Key 放到 URL 或公开 Skill 中。Codex 的辅助脚本不适用于其他客户端；具体版本的配置位置需核对，不能宣称 OpenClaw/Hermes 已验证。
