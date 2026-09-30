# Agent Skills

面向 AI 助手的可复用工作流程。每个 Skill 独立存放，按需安装。

## Skill 目录

| Skill | 用途 | 接入要求 |
|---|---|---|
| [cinevault-query](skills/cinevault-query/SKILL.md) | 查询映藏 CineVault 的电影、剧集、资源版本与收录统计 | 已连接 CineVault 普通 MCP，并取得独立访问凭据 |

## 安装

需要可运行 `npx` 的 Node.js/npm 环境，使用 [skills CLI](https://github.com/vercel-labs/skills)。

查看可用 Skill：

```bash
npx skills add xiongwei-git/agent-skills --list
```

安装映藏查询 Skill：

```bash
npx skills add xiongwei-git/agent-skills --skill cinevault-query
```

指定客户端，例如 Codex：

```bash
npx skills add xiongwei-git/agent-skills --skill cinevault-query -a codex
```

默认安装范围及可选客户端以 CLI 提示为准。也可下载所需 Skill 的完整目录，按客户端支持的方式安装。复制时保留该目录内的 references、scripts 等资源（如有）。

## CineVault 接入状态

Skill 提供操作流程，不包含 MCP 服务端，不会自动部署服务或生成访问凭据。

CineVault 当前为邀请使用，尚未提供公共 MCP 地址或公开申请渠道。已有授权的使用者需在客户端配置管理员提供的普通 MCP 地址及凭据后才能实际查询。普通端点路径为 `/mcp`；不要把其他机器上的 `127.0.0.1` 地址当成自己可访问的远程服务。

凭据只保存在客户端支持的秘密存储或私密环境中，不写入 Skill、Git、URL、安装命令或聊天。此仓库不分发管理员 Skill、服务端源码、数据库或凭据。

Skill 文件结构已经校验；安装器能识别目录不代表具体客户端的 MCP 连接与业务查询已验收。OpenClaw、Hermes 的实际接入兼容性仍待验证。

## 维护

新增 Skill 使用 `skills/<skill-name>/SKILL.md`，每个目录独立包含必要资源。业务 Skill 在对应业务项目中维护和验证，再将可公开的版本同步至本仓库。不要在两个位置分别修改同一 Skill 后直接覆盖。

安装行为与支持的选项参见 [skills CLI 文档](https://github.com/vercel-labs/skills)。本仓库尚未声明开源许可证。
