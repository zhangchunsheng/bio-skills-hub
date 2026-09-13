---
name: ttfund-innovative-pharma
description: >
  分析港股通创新药赛道的中长期配置价值、短期信号、行业基本面、估值和风险，并支持创新药 ETF 产品对比。适合“港股创新药值得配置吗”“创新药 ETF 怎么选”等问题。 通过共享 ttskill CLI 按需安装并调用 TTFUND_INNOVATIVE_PHARMA；底座已存在时不得重复安装。
---

# 天天港股创新药分析

这是天天基金 `TTFUND_INNOVATIVE_PHARMA` 的独立原子入口。输出港股创新药赛道多维度分析、星级结论及 ETF 对比；不展示内部权重和字段名，不构成收益保证。

## 典型触发

- “港股通创新药现在值得配置吗”
- “分析创新药赛道的中长期机会”
- “对比几只港股创新药 ETF”

## 按需安装底座与业务包

按以下顺序主动执行，不要把安装步骤转交给用户：

1. 运行 `ttskill --version`。若命令暂时不在 PATH，先检查 `$HOME/.local/bin/ttskill` 等基础包标准长期入口并刷新当前进程 PATH；只有确认可执行文件确实不存在或损坏后才进入第 2 步。命令可用即视为共享 CLI 底座已安装，跳过底座安装；不要因当前原子业务包缺失而重装底座。
2. 仅当 `ttskill` 命令不存在或损坏时，解析系统平台与架构，再请求官方基础包解析接口：
   `https://skills.tiantianfunds.com/ai-smart-skill-service/openapi/base-package/resolve?platform={platform}&arch={arch}&env=prod`。
   平台映射使用 Windows x64=`win32/x64`、macOS Apple Silicon=`darwin/arm64`、macOS Intel=`darwin/x64`、Linux x64=`linux/x64`。读取响应的 `data.download_url` 下载到临时目录；若响应提供 SHA-256 则先校验；解压后执行包内当前平台安装脚本。安装完成后重新确认 `ttskill --version` 和 `ttskill status --env prod --json`。若 PATH 尚未刷新，Unix 将 `$HOME/.local/bin` 加入当前进程 PATH，Windows 刷新当前用户 PATH。
3. 基础包首次安装只完成 CLI 底座。不要同步或安装全部 33 个业务包，也不要重复创建总入口。
4. 运行 `ttskill skill info TTFUND_INNOVATIVE_PHARMA --json`。若返回已启用的安装信息，直接复用；若目标业务包缺失，只执行：
   `ttskill install TTFUND_INNOVATIVE_PHARMA --env prod`。
5. 如果安装或调用明确报告版本过旧，只更新当前业务包：
   `ttskill update TTFUND_INNOVATIVE_PHARMA --env prod`。
   不要借机全量更新其他业务包。

## 登录与调用

1. 运行 `ttskill status --env prod --json` 检查 `auth.has_token`。若未登录、登录过期，或调用返回 `cli_login_required`，主动执行 `ttskill login --env prod` 拉起扫码或授权；已登录时不要重复登录。
2. 再次执行 `ttskill skill info TTFUND_INNOVATIVE_PHARMA --json`，从 `install_path` 定位当前安装版本。完整阅读其中的 `SKILL.md`，并按需读取 `examples/*.example.json`；它们是当前 action、请求参数、返回字段和业务边界的唯一权威说明。
3. 根据该业务文档调用：
   `ttskill invoke TTFUND_INNOVATIVE_PHARMA --action <action> --env prod --body <json_or_file>`。
   需要完整业务分析时不要默认添加 `--summary`；复杂 JSON 优先写入临时文件，避免 shell 引号错误。
4. 提炼核心业务结果，标明必要的数据时点与风险提示，不输出 token、cookie、设备密钥、完整银行卡号或原始大段 JSON。

## 边界

- 只安装和调用 `TTFUND_INNOVATIVE_PHARMA`，不要用分类名或相邻 Skill 猜 action 与参数。
- 不配置或索取 `TTFUND_APIKEY`，不使用 `X-API-Key`、旧 Cookie、手工 token 或旧 API Key 流程。
- 不把账户、行情或筛选结果表述为收益承诺；市场有风险，投资需谨慎。
