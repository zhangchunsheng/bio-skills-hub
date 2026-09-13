---
name: zkteco-att-push-protocol
description: "熵基科技（ZKTeco）考勤 PUSH 通讯协议 V5.8 专业参考 skill。触发场景：(1) 用户询问考勤设备对接方式、URL 路径、参数含义；(2) 需要解析考勤记录/操作记录/异常日志等数据格式；(3) 需要了解设备上传数据的 16 种类型及字段定义；(4) 需要查找 DATA UPDATE/DELETE/QUERY 子命令（20 种 UPDATE / 13 种 DELETE / 5 种 QUERY）的字段定义；(5) 需要实施远程登记（ENROLL_FP/ENROLL_MF/ENROLL_BIO）；(6) 需要在线升级或后台验证；(7) 需要实现 PUSH 服务端（Python/Java）框架。不适用于门禁（acc）、停车（park）、消费（pos）等非考勤协议场景。"
---

# ZKTeco 考勤 PUSH 通讯协议专业参考（V5.8 / PUSH V2.4.2）

## 概述

提供熵基科技（ZKTeco）考勤 PUSH 通讯协议 V5.8（PUSH 协议版本 V2.4.2）的完整专业参考。该协议基于 **HTTP 1.1（TCP/IP）**，适用于考勤设备（标准考勤/人证核验/信息屏）与服务端之间的数据交互。**所有行为由设备端发起**。

### 核心特征

- 设备主动发起 HTTP 请求，服务端被动响应
- 编码：UTF-8（用户姓名字段在中文设备上使用 GB2312）
- 分隔符：字段间使用制表符 `\t`（HT），记录间使用换行符 `\n`（LF）
- 子协议：`att`（标准考勤）/ `pid`（人证核验）/ `ins`（信息屏）
- 通信加密：PUSH 协议版本 ≥ 2.4.0 支持（DH 密钥交换 + sessionKey 对称加密）

### 与安防 PUSH 的主要区别

| 对比项 | 考勤 PUSH V5.8 | 安防 PUSH V7.3 |
|--------|---------------|---------------|
| PUSH 协议版本 | V2.4.2 | V3.1.2 |
| 设备注册 | 无独立注册步骤 | 有 `/iclock/registry` 流程 |
| 命令获取 | `GET /iclock/getrequest` | `POST /iclock/push` |
| 配置下发 | 初始化时直接返回 | 独立 `/iclock/push` |
| 核心数据 | 考勤记录/照片 | 门禁事件/状态 |
| 身份证功能 | 支持（人证协议） | 不支持 |
| Token 机制 | 仅 ping 使用 | push 请求均使用 |

---

## 快速定位指南

### API 接口速查

**设备→服务器上传接口：**

| HTTP 方法 | URL 路径 | 功能 | 说明 |
|-----------|---------|------|------|
| `GET` | `/iclock/cdata?SN={SN}&options=all` | 初始化信息交互 | 必选，首次连接 |
| `POST` | `/iclock/exchange?SN={SN}&type=publickey` | 交换公钥 | 可选（加密时用） |
| `POST` | `/iclock/exchange?SN={SN}&type=factors` | 交换因子 | 可选（加密时用） |
| `POST` | `/iclock/cdata?SN={SN}&table=options` | 推送配置参数 | 可选 |
| `GET` | `/iclock/getrequest?SN={SN}&INFO=...` | 上传更新信息 + 获取命令 | 可选/必选 |
| `GET` | `/iclock/ping?SN={SN}` | 心跳 | 推荐 |
| `POST` | `/iclock/cdata?SN={SN}&table=ATTLOG` | 上传考勤记录 | 核心 |
| `POST` | `/iclock/cdata?SN={SN}&table=ATTPHOTO` | 上传考勤照片 | 可选 |
| `POST` | `/iclock/cdata?SN={SN}&table=OPERLOG` | 上传操作记录/用户/模板等 | 多用途 |
| `POST` | `/iclock/cdata?SN={SN}&table=IDCARD` | 上传身份证信息 | 人证协议 |
| `POST` | `/iclock/cdata?SN={SN}&table=BIODATA` | 上传一体化模板 | 混合识别 |
| `POST` | `/iclock/cdata?SN={SN}&table=ERRORLOG` | 上传异常日志 | PUSH ≥ 2.4.1 |
| `POST` | `/iclock/devicecmd?SN={SN}` | 命令回复 | 收到命令后必回 |
| `GET` | `/iclock/cdata?SN={SN}&table=RemoteAtt&PIN={PIN}` | 异地考勤 | 可选 |

**服务器→设备命令格式：**

所有命令通过设备轮询 `GET /iclock/getrequest?SN={SN}` 下发：

```
C:{CmdID}:{命令类型} {参数}
```

### 命令类型速查

| 命令类型 | 功能分类 | 子命令数 | 说明 |
|----------|---------|---------|------|
| `DATA UPDATE` | 新增/修改数据 | 20 种 | 用户/模板/照片/消息/门禁等 |
| `DATA DELETE` | 删除数据 | 13 种 | 按条件删除 |
| `DATA QUERY` | 查询数据 | 5 种 | 考勤记录/照片/用户/模板 |
| `CLEAR` | 清除数据 | 5 种 | LOG/PHOTO/DATA/BIODATA/ALL USERINFO |
| `CHECK/LOG` | 检查命令 | 3 种 | 数据更新/传送/校对 |
| `SET OPTION/RELOAD OPTIONS/INFO` | 配置选项 | 3 种 | |
| `GetFile/PutFile` | 文件命令 | 2 种 | |
| `ENROLL_FP/ENROLL_MF/ENROLL_BIO` | 远程登记 | 3 种 | |
| `REBOOT/AC_UNLOCK/AC_UNALARM` | 控制命令 | 3 种 | |
| `SHELL/UPGRADE` | 其他命令 | 2 种 | 系统命令/升级/后台验证 |

### 附录速查

| 附录 | 内容 | 用途 |
|------|------|------|
| 附录1 | 通用错误码 | Return 值含义排查 |
| 附录2 | 语言编号 | language 参数取值 |
| 附录3 | 操作代码 | OPERLOG 的 OpType 含义 |
| 附录5 | 报警原因 | 报警事件解析 |
| 附录6 | 协议版本规则 | pushver 版本协商 |
| 附录7 | 验证方式码 | Verify 字段取值 (0-29+200) |
| 附录8 | 通信加密方案 | 密钥交换流程 |
| 附录9 | 异常日志错误码 | ERRORLOG 的 ErrCode 解析 |
| 附录10 | 生物识别类型索引 | Type 字段 (0-10) 含义 |

---

## 使用流程

### 第一步：理解协议体系

1. 确认协议版本（文档 V5.8 / PUSH 协议 V2.4.2）
2. 查看 **API 接口速查** 表了解所有 HTTP 接口
3. 阅读 **通信流程** 了解整体交互顺序

### 第二步：实现服务器端基本框架

标准对接顺序：

1. **初始化信息交互** → 实现 `GET /iclock/cdata?options=all` 处理
2. **心跳** → 实现 `GET /iclock/ping` 处理
3. **上传数据** → 实现 `POST /iclock/cdata` 处理（至少 ATTLOG）
4. **命令获取** → 实现 `GET /iclock/getrequest` 命令队列
5. **命令回复** → 实现 `POST /iclock/devicecmd` 处理

### 第三步：处理具体数据

- **上传考勤记录**：table=ATTLOG → 解析 Tab 分隔字段（Pin/Time/Status/Verify...）
- **上传考勤照片**：table=ATTPHOTO → 解析照片元数据 + 二进制流
- **上传操作记录**：table=OPERLOG → 解析 OPLOG 格式
- **上传用户信息**：table=OPERLOG → 解析 USER 格式
- **上传指纹/面部/指静脉模板**：table=OPERLOG → 解析 FP/FACE/FVEIN 格式
- **上传一体化模板**：table=BIODATA → 解析 BIODATA 格式
- **上传异常日志**：table=ERRORLOG → 解析 ErrCode

### 第四步：下发命令

- **下发用户信息**：`DATA UPDATE USERINFO`
- **下发指纹模板**：`DATA UPDATE FINGERTMP`
- **下发面部模板**：`DATA UPDATE FACE`
- **下发一体化模板**：`DATA UPDATE BIODATA`
- **下发比对照片**：`DATA UPDATE BIOPHOTO`
- **删除数据**：`DATA DELETE {TableName}`
- **查询数据**：`DATA QUERY {TableName}`

### 第五步：高级功能

- **远程登记**：ENROLL_FP / ENROLL_MF / ENROLL_BIO
- **在线升级**：UPGRADE（支持三种方式）
- **后台验证**：PostVerifyData
- **异地考勤**：RemoteAtt

---

## 代码生成指南

### Python PUSH 服务端框架

在 `assets/att_push_demo.py` 中提供完整的 PUSH 服务端参考实现，包括：

| 功能 | 文件/函数 |
|------|----------|
| HTTP 服务端骨架 | `AttPushServer` 类 |
| 初始化处理 | `handle_cdata_options()` |
| 数据上传处理 | `handle_cdata_upload()` |
| 命令获取处理 | `handle_getrequest()` |
| 命令回复处理 | `handle_devicecmd()` |
| 心跳处理 | `handle_ping()` |

### 生成集成代码

当第三方公司提出以下需求时，参考对应章节生成代码：

| 用户需求 | 参考章节 | 参考代码 |
|---------|---------|---------|
| "接收考勤记录" | 9.1 上传考勤记录 | `parse_attlog_record()` |
| "接收考勤照片" | 9.2 上传考勤照片 | `parse_attphoto()` |
| "下发用户信息" | 10.1.1 用户信息 | `build_userinfo_cmd()` |
| "下发指纹模板" | 10.1.3 指纹模板 | `build_fingertmp_cmd()` |
| "查询考勤记录" | 10.3.1 考勤记录查询 | `build_query_attlog_cmd()` |

### 代码规范

- 所有示例代码使用 Python 3.8+
- 依赖仅限标准库（http.server, urllib, json, base64 等）
- 代码中关键路径和字段使用注释标明参考章节号
- 错误处理和边界情况包含注释说明

---

## 参考文档

完整的协议参考文档位于 `references/att-push-v58-reference.md`，包含：

- 全部 16 种上传数据格式的字段定义和示例
- 全部 DATA UPDATE（20 种）/ DELETE（13 种）/ QUERY（5 种）子命令的完整字段定义
- 全部 3 种远程登记命令的格式和返回值
- 全部 10 个附录的完整枚举值表
- 全部控制命令、检查命令、配置命令、文件命令的格式
- 通信加密方案（DH 密钥交换）详细流程
- 混合识别协议规范说明
- 与安防 PUSH 协议差异对比表
- 对接注意事项（编码、数据量、卡号格式等）

---

## 示例代码资产

`assets/att_push_demo.py` 提供可直接运行的 PUSH 服务端示例：

```bash
# 启动服务端（默认端口 8088）
python att_push_demo.py

# 服务端日志输出示例
[INIT] SN=0316144680030 - 初始化成功，返回配置参数
[UPLOAD] SN=0316144680030 - 收到考勤记录 9 条
[UPLOAD] SN=0316144680030 - 收到操作记录 1 条
[HEARTBEAT] SN=0316144680030 - 心跳 OK
```

---

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 设备返回 `Return=-1` | 参数格式错误 | 检查字段名、分隔符（\t 制表符）是否正确 |
| 设备返回 `Return=-10` | 指定 PIN 的用户不存在 | 确认用户已下发 |
| 设备返回 `Return=-30` | 一体化模板算法版本不一致 | 检查 MajorVer/MinorVer |
| 设备不连接 | IP/端口配置错误 | 确认 `ErrorDelay` 设置合理（建议 30-300 秒） |
| 考勤记录上传为 0 | TransFlag 未配置 | 设置 TransFlag 包含 AttLog |
| 中文姓名乱码 | 编码问题 | 中文设备使用 GB2312，其他使用 UTF-8 |
| 照片上传失败 | 数据量过大 | 单次下发数据量不得超过 900KB |

## 📞 帮助与支持

- 联系微信 <u>Principles_RD</u>（备注协议对接）获得技能使用支持；
