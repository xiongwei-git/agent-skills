# Agent Skills

面向 AI 助手的可复用工作流程。每个 Skill 独立存放，按需安装。

## Skill 目录

| Skill | 用途 | 接入要求 |
|---|---|---|
| [cinevault-query](skills/cinevault-query/SKILL.md) | 查询映藏 CineVault 的电影、剧集、资源版本与收录统计 | 安装后首次配置管理员提供的普通API Key，正式地址已预置 |

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

Skill 提供查询流程及首次接入引导。首次使用时提示配置普通 API Key，目录内的 Python 标准库脚本负责验证并注册 Codex 普通连接，不需另装安装器。服务端与访问资格由管理员提供。

CineVault 当前为邀请使用，正式普通入口已预置为 `https://cinevault.tedxiong.com/mcp`，首页为 `https://cinevault.tedxiong.com`。首次接入只需管理员提供的普通API Key，不要求用户填写地址。正式域名已配置在Skill中，服务部署和HTTPS反代仍需以实际在线校验为准，不能仅凭安装成功宣称服务可用。

管理员申请的普通Key保存在服务端数据库，默认3个日历月有效、次数不限；显式次数为有效期内累计上限。普通客户端首次保存自己的Key后即可查询。电影名称必填且非空，支持中文名/原名模糊匹配；空库或尚未收录时正常返回空结果。轮播占位不代表收录。

仅本机研发测试才追加 `--url http://127.0.0.1:18765/mcp`，正常使用不用URL参数。已有客户端配置不会因更新Skill自动覆盖；若原先使用本机测试地址，切换正式服务需按连接说明处理已有私密配置。

凭据只保存在客户端支持的秘密存储或私密环境中，不写入 Skill、Git、URL、安装命令或聊天。此仓库不分发管理员 Skill、服务端源码、数据库或凭据。

首次接入详见 [连接说明](skills/cinevault-query/references/connect.md)。Key 在终端隐藏输入或从权限600的私密文件读取，不发到聊天中；配置存于用户本机 ~/.config/cinevault/reader.json（600）。配置后可能需要新开聊天加载工具。

Skill 结构、辅助脚本的隔离连接/注册/只读调用/错误授权测试已经通过；具体用户的 MCP 连接与业务查询仍须验收。OpenClaw、Hermes 的实际接入兼容性仍待验证。

## 维护

新增 Skill 使用 `skills/<skill-name>/SKILL.md`，每个目录独立包含必要资源。业务 Skill 在对应业务项目中维护和验证，再将可公开的版本同步至本仓库。不要在两个位置分别修改同一 Skill 后直接覆盖。

安装行为与支持的选项参见 [skills CLI 文档](https://github.com/vercel-labs/skills)。本仓库尚未声明开源许可证。
