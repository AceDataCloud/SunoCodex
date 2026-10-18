# Codex 的 Suno by Ace Data Cloud

通过 Ace Data Cloud 在 Codex 使用音乐生成、歌词、续写与翻唱。这是独立服务插件，复用现有托管 MCP；不冒充服务品牌或 OpenAI 官方插件。

[English](../README.md) · [注册/登录](https://platform.acedata.cloud/?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=sunocodex_readme_register_zh) · [价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=sunocodex_readme_pricing_zh)

## 1. 安装

目标是在 Codex 官方插件目录搜索 **Suno**，选择 **Suno by Ace Data Cloud** 并安装。当前官方尚未收录；源码 PR、第三方目录安装与官方上线分开。

评估候选包时，用 Codex 0.163.0 或更高版本执行：

```bash
codex plugin marketplace add AceDataCloud/SunoCodex --ref codex/native-service-20261018
codex plugin add suno@acedatacloud-suno --json
```

加入的是该服务的第三方目录；安装后仅启用Suno。在原生插件界面选择刚加入的目录，按服务名搜索并核对发布者 Ace Data Cloud；本轮没有界面实拍验收。

## 2. 获取与配置 API Token

1. [登录 Ace → Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=sunocodex_readme_api_key_zh)；没有 General application 时先初始化。
2. 打开 **General application**，确认当前服务权限、价格和余额。复制 API Key，或 **Manage Keys → Create** 创建名为 `Codex Suno` 的独立凭据。

![真实平台截图：复制 Key 或 Manage Keys](../assets/get-api-key-en.png)

3. 按需要设有效期、使用限额和 Allowed APIs，至少覆盖要调用的生成与查询路径 `/suno/audios`、`/suno/tasks`。不自动扩大权限。

![真实平台截图：创建凭据](../assets/create-api-key-en.png)

原图来自 SunoDify，凭据已遮盖，2026-10-18 核对。创建框中的 Dify 名称是旧例子，请换成 Codex 服务名。只复制真实的原始 Key，不带 `Bearer `；平台管理 token 不能替代。

在启动 Codex 的终端设置：

```bash
export ACEDATACLOUD_API_TOKEN="你的服务 API Key"
codex
```

PowerShell 用 `$env:ACEDATACLOUD_API_TOKEN = "你的服务 API Key"`。进入新会话，运行 `/mcp` 看连接和工具；无需另写 MCP 地址。桌面启动的进程也必须继承变量。不要将 Key 放入提示词、截图、共享配置或 Git。

![Codex 官方原始参考图，非 Ace 运行](../assets/codex-official-reference.png)

这是 Codex 官方界面参考，仅显示终端输入与结果区域，不证明插件已安装或 Ace 已运行；原文件最后更新 2026-01-02。来源和边界见 [sources](../assets/sources.json)。真实插件搜索/安装/免费调用画面由协调者排队拍摄，不使用假界面。

## 3. 首次调用与结果

先请求调用 `suno_list_models` 查看说明，不提交生成。

要生成或编辑时，先确认当前价格、模型/操作和额度，再提交一次。保存 task ID，之后用 `suno_get_task` 查询同一 ID 到成功或失败。Pending 不是成品，不要为查询而重新生成；成功后打开返回媒体，再核对同一请求的使用记录。这里不声称已完成收费生成或账单验收。

## 常见问题

401：变量未传入、Key类型或有效期错误；403：权限/Allowed APIs；429：等待并减少并发，勿自动重试收费提交；pending：查原ID；400：核实当前工具schema；5xx/超时：保留task/trace ID，先查原状态。官方搜不到：当前候选尚未收录，不能把第三方安装称官方上线。

插件免费，API按账户当前规则计费，Key和所选输入发送至Ace托管服务。支持：dev@acedata.cloud；[源码](https://github.com/AceDataCloud/SunoCodex)；[隐私](../PRIVACY.md)。
