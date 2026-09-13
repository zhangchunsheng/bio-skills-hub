# 生物多样性风险助手 - 在线服务 API 参考

本技能通过 `scripts/mcp_client.py` 直调「生物多样性风险助手」服务，**无需配置任何连接器**。本文档为技术参考，供排查问题或扩展使用。

## 1. 服务信息

| 项目 | 值 |
|------|------|
| 端点 | `https://mid.shanshui.org/biodiversity-mcp/mcp` |
| 协议 | MCP (Model Context Protocol) over HTTP，streamable-http |
| 认证 | HTTP Header `Authorization: Bearer <API Key>` |
| 最新协议版本 | `2025-03-26` |

## 2. 鉴权（两级 Key 模式）

- 所有请求必须在 Header 中携带：`Authorization: Bearer <API Key>`。
- Key 缺失或无效时返回 **HTTP 401**。
- 凭证分两级：
  - **公共 Key（内置兜底）**：已写入 `scripts/mcp_client.py` 的 `PUBLIC_KEY` 常量，零配置自动使用，提供基础功能（由服务端限流控制）。
  - **私有 Key（增强）**：请联系山水自然保护中心获取（见 `mcp_config.md`），提供更强功能与更高配额。
- Key 优先级：`--token` 参数 > 环境变量 `BIODIVERSITY_MCP_TOKEN` > `state/api_key.txt`（私有 Key）> 内置公共 Key。
- 401 时脚本会按当前 Key 类型输出提示：公共 Key 模式（可能被更新/限流，建议申请私有 Key）或私有 Key 模式（Key 无效/过期）。

## 3. 调用协议（标准 MCP 握手）

调用链为三次 HTTP POST（AI 无需手写，直接使用 `scripts/mcp_client.py` 即可）：

1. **initialize** — 建立会话，响应头 `Mcp-Session-Id` 为会话 ID；
2. **notifications/initialized** — 通知服务端已完成初始化（无响应体）；
3. **tools/list** 或 **tools/call** — 后续所有请求需携带 `Mcp-Session-Id` 请求头。

请求头示例：

```
Content-Type: application/json
Accept: application/json, text/event-stream
Authorization: Bearer <API Key>
Mcp-Session-Id: <initialize 返回的会话 ID>   // 第 3 步起携带
```

## 4. 工具清单

### 4.1 `check_project_compliance` — 项目合规风险核查

- 用途：检查建设项目是否符合生物多样性保护相关要求。
- 参数：
  - `name` (string)：项目名称（推荐）
  - `lng` / `lat` (number)：项目经纬度（可选，但强烈建议提供，用于精确定位）
  - `address` (string)：项目地址（可选）
- 行为：优先按 `name` 匹配本地环评项目库；查不到且无坐标时，返回的 `delegate.instruction` 会要求按 TNFD LEAP 的 Locate 步骤追问坐标/地址。

### 4.2 `nature_disclosure_advice` — TNFD 自然信息披露建议

- 用途：按 TNFD 框架生成自然相关信息披露建议（对齐 TNFD LEAP）。
- 参数：同 `check_project_compliance`。
- 行为：返回事实数据作为披露依据，披露建议文案需结合 `delegate.skill_content` 生成。

### 4.3 `biodiversity_increment_suggestions` — 生多公益增量建议

- 用途：提供生物多样性公益增量项目建议。
- 参数：
  - `context` (string)：项目/企业背景描述（必填）
- 行为：服务无对应数据/算法时，`data` 可能为空——**AI 必须结合 `delegate.skill_content` 与用户上下文给出兜底建议，不得拒答**。

### 4.4 `get_biodiversity_expert_skill` — 获取专家知识框架

- 用途：单独获取生物多样性专家知识框架全文（`skills/biodiversity-expert.md`）。
- 参数：无。

## 5. 返回结构

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      { "type": "text", "text": "{ ...JSON 字符串... }" }
    ]
  }
}
```

`content[0].text` 为 JSON 字符串，解析后为 **delegate 结构**：

| 字段 | 说明 |
|------|------|
| `data` | 事实数据（查询结果；可能为空对象，空不代表无结果） |
| `delegate.instruction` | 对 AI 的执行指令（如要求追问坐标后重新调用） |
| `delegate.skill_content` | 领域知识/兜底建议素材，AI 须结合其推理回答 |

## 6. 错误码与排查

| 现象 | 含义 | 处理 |
|------|------|------|
| HTTP 401（公共 Key 模式） | 公共 Key 已被更新、吊销或触发限流 | 联系山水自然保护中心申请私有 Key |
| HTTP 401（私有 Key 模式） | 私有 Key 无效或过期 | 检查 `state/api_key.txt` 内容；重新申请 |
| 输出 `NO_KEY:` | 未找到 Key（v1.2.0 起不再出现，自动回退公共 Key） | 升级技能版本；或设置环境变量 `BIODIVERSITY_MCP_TOKEN` |
| `initialize 失败` | 网络不通或服务异常 | 检查网络；稍后重试 |
| `TOOL_ERROR` | 参数不合法或服务端错误 | 检查参数名/类型；查看错误详情 |
| 超时 | 服务响应慢 | 增加超时重试一次 |

## 7. 命令行用法速查

```bash
# 列出工具（兼作 Key 连通性检查）
python scripts/mcp_client.py list

# 调用工具（Key 自动按优先级读取：私有 Key > 内置公共 Key）
python scripts/mcp_client.py call check_project_compliance --name "XX项目" --lng 116.4 --lat 39.9
python scripts/mcp_client.py call biodiversity_increment_suggestions --context "..."

# 临时用 --token 覆盖（如切换到另一个私有 Key）
python scripts/mcp_client.py call check_project_compliance --name "XX项目" --token <KEY>
```

> 脚本为纯 Python 标准库实现，`python` / `python3` 均可运行，无需安装任何第三方包。
