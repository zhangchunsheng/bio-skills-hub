# 05 SBOM 实操

> 用途：回答「SBOM 怎么建？包含哪些字段？用什么格式？怎么维护？」。
> 核对基准日：2026-08-27

## 1. SBOM 是什么、为什么强制

- **SBOM（Software Bill of Materials，软件物料清单）**：一份机器可读的组件清单，列出器械软件里所有直接与间接成分——专有、商业、开源（OSS）、现成（OTS）组件及版本；
- **FDA**：§524B 对 cyber devices 的**法定强制**要求，缺失 = RTA 拒绝受理；
- **欧盟 CRA**：要求保持更新的机器可读 SBOM（至少顶层依赖），供市场监管机构索取；
- **价值**：组件一旦爆漏洞（如 Log4j 式事件），有 SBOM 才能快速定位受影响产品并出补丁。

## 2. 字段要求（NTIA 最低要素，三大要求）

NTIA（美国商务部国家电信和信息管理局）最低要素，是 FDA 认可基线：

| 字段 | 说明 |
|---|---|
| 供应商名称 | Supplier Name |
| 组件名称 | Component Name |
| 组件版本 | Version of the Component |
| 组件唯一标识 | Component Hash（含哈希算法） |
| 依赖关系 | Relationship（组件间依赖） |
| 作者 | Author of the SBOM Data |
| 时间戳 | Timestamp |

FDA 额外建议：**支持状态（support status）与停止支持日期（end-of-support date）**、已知漏洞核查（对照 CISA KEV）。

## 3. 格式选择（SPDX vs CycloneDX）

| 维度 | SPDX | CycloneDX |
|---|---|---|
| 出身 | Linux Foundation | OWASP |
| 强项 | 许可证合规、版权 | 漏洞管理、与 VEX 集成 |
| 适合场景 | 注重许可审计 | 注重安全/漏洞跟踪 |
| FDA 立场 | 均可（机器可读即可） | 均可 |

建议：以**漏洞管理为主要目的**用 CycloneDX（配 VEX），以**许可证合规为主**用 SPDX；两者可共存。

## 4. 构建流程（六步）

1. **盘点软件栈**：OS、运行时、第三方库、中间件、固件、驱动、OTA 组件——全生命周期收集；
2. **选择工具链**：构建期自动生成（如 CycloneDX 官方工具链、GitHub SBOM 导出、商用 BOM 工具），避免手工维护；
3. **生成 SBOM**：每个发布版本生成对应 SBOM，存版本库，与软件版本绑定；
4. **做漏洞匹配**：SBOM 组件清单 → 对照 CISA KEV、NVD、厂商公告，识别已知漏洞；
5. **输出 VEX**（可选但推荐）：漏洞利用性交换（Vulnerability Exploitability eXchange），说明每个漏洞的状态（受影响/不受影响/已修复/正在调查）；
6. **随申报提交**：FDA 提交中附机器可读 SBOM + 漏洞分析说明。

## 5. 维护与更新

- **每次发布更新**：SBOM 必须与提交的软件版本一致——测试报告与版本不匹配是 FDA 高频缺陷；
- **组件变更流程**：升级/替换组件 → 重新生成 SBOM → 重新做漏洞匹配 → 影响分析（是否触发网络安全更新申报）；
- **供应商协同**：对 OTS/商业组件，要求供应商提供其组件的 SBOM（契约条款里写清楚），FDA 对「相关系统」同样关注；
- **生命周期管理**：记录每个组件的支持状态与停止支持日期，制定替换计划（停止支持的组件是审评关注点）。

## 6. 工具入口

`python tools/meddev_cyber_toolkit.py sbom` 输出 SBOM JSON 字段模板（NTIA 最低要素 + FDA 补充字段）。
