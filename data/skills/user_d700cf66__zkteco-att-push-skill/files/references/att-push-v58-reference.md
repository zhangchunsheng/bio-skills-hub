# 考勤 PUSH 通讯协议 V5.8 —— 对接说明

> 协议版本：PUSH V2.4.2 | 文档版本：V5.8（2026-03）
> 适用场景：第三方服务器/平台对接熵基考勤设备（标准考勤 / 人证核验 / 信息屏）

---

## 目录

- [1. 协议概述](#1-协议概述)
- [2. 通信流程](#2-通信流程)
- [3. 初始化信息交互](#3-初始化信息交互)
- [4. 交换公钥（通信加密）](#4-交换公钥通信加密)
- [5. 交换因子（通信加密）](#5-交换因子通信加密)
- [6. 推送配置信息](#6-推送配置信息)
- [7. 上传更新信息](#7-上传更新信息)
- [8. 心跳](#8-心跳)
- [9. 上传数据](#9-上传数据)
  - [9.1 上传考勤记录](#91-上传考勤记录)
  - [9.2 上传考勤照片](#92-上传考勤照片)
  - [9.3 上传操作记录](#93-上传操作记录)
  - [9.4 上传用户信息](#94-上传用户信息)
  - [9.5 上传身份证信息（仅人证协议）](#95-上传身份证信息仅人证协议)
  - [9.6 上传身份证考勤记录（仅人证协议）](#96-上传身份证考勤记录仅人证协议)
  - [9.7 上传身份证考勤照片（仅人证协议）](#97-上传身份证考勤照片仅人证协议)
  - [9.8 上传指纹模板](#98-上传指纹模板)
  - [9.9 上传面部模板](#99-上传面部模板)
  - [9.10 上传指静脉模板](#910-上传指静脉模板)
  - [9.11 上传一体化模板](#911-上传一体化模板)
  - [9.12 上传用户照片](#912-上传用户照片)
  - [9.13 上传数据包](#913-上传数据包)
  - [9.14 上传比对照片（仅可见光设备）](#914-上传比对照片仅可见光设备)
  - [9.15 上传异常日志](#915-上传异常日志)
- [10. 获取命令](#10-获取命令)
  - [10.1 DATA UPDATE 子命令](#101-data-update-子命令)
  - [10.2 DATA DELETE 子命令](#102-data-delete-子命令)
  - [10.3 DATA QUERY 子命令](#103-data-query-子命令)
  - [10.4 CLEAR 命令](#104-clear-命令)
  - [10.5 检查命令](#105-检查命令)
  - [10.6 配置选项命令](#106-配置选项命令)
  - [10.7 文件命令](#107-文件命令)
  - [10.8 远程登记命令](#108-远程登记命令)
  - [10.9 控制命令](#109-控制命令)
  - [10.10 其他命令](#1010-其他命令)
- [11. 命令回复](#11-命令回复)
- [12. 异地考勤](#12-异地考勤)
- [13. 附录](#13-附录)

---

## 1. 协议概述

考勤 PUSH 协议基于 **HTTP 1.1**，建立在 **TCP/IP** 连接之上，用于熵基考勤设备与服务器的数据交互。

**核心特征：**
- 所有行为由**设备（客户端）** 主动发起
- 设备轮询获取服务器下发的命令（`/iclock/getrequest`）
- 数据编码统一使用 **UTF-8**（中文环境下用户姓名使用 GB2312）
- 字段分隔符使用制表符 `\t`（HT），多条记录之间使用换行符 `\n`（LF）
- 支持**通信加密**（push 协议版本 2.4.0 及以上）
- 支持三种子协议：`att`（标准考勤）、`pid`（人证协议）、`ins`（信息屏协议）

**子协议类型（DeviceType 参数）：**

| 取值 | 子协议 | 说明 |
|---|---|---|
| `att` | 标准考勤协议 | 默认 |
| `pid` | 人证协议 | 支持身份证相关功能 |
| `ins` | 信息屏协议 | 信息屏设备 |

**协议交互图：**

```
┌──────────────┐                               ┌───────────────┐
│  设备（客户端）  │   ── ① 初始化请求 ──►        │   服务器       │
│              │   ◄── 配置参数 ──              │               │
│              │   ── ② 推送配置（可选）──►      │               │
│              │   ── ③ 上传数据 ──►            │  解析/存储     │
│              │   ── ④ 心跳(ping) ──►         │  保持连接      │
│              │   ── ⑤ 获取命令 ──►            │               │
│              │   ◄── 下发命令 ──              │  控制设备      │
│              │   ── ⑥ 命令回复 ──►            │               │
└──────────────┘                               └───────────────┘
```

---

## 2. 通信流程

完整的通信生命周期：

```
步骤1： 初始化信息交互    GET /iclock/cdata?SN=xxx&options=all&pushver=xxx
        └── 服务器返回配置参数（Stamp、ErrorDelay、Delay、TransFlag 等）

步骤2（可选）：交换公钥    POST /iclock/exchange?SN=xxx&type=publickey
步骤3（可选）：交换因子    POST /iclock/exchange?SN=xxx&type=factors

步骤4（可选）：推送配置    POST /iclock/cdata?SN=xxx&table=options
        └── 设备主动推送功能开关等配置

步骤5： 循环执行
        ├── 上传更新信息  GET /iclock/getrequest?SN=xxx&INFO=xxx
        ├── 上传考勤记录  POST /iclock/cdata?SN=xxx&table=ATTLOG
        ├── 上传考勤照片  POST /iclock/cdata?SN=xxx&table=ATTPHOTO
        ├── 上传操作记录  POST /iclock/cdata?SN=xxx&table=OPERLOG
        ├── 心跳          GET /iclock/ping?SN=xxx
        ├── 获取命令      GET /iclock/getrequest?SN=xxx
        └── 命令回复      POST /iclock/devicecmd?SN=xxx
```

**上传方式（三选一，实时优先）：**

| 方式 | 说明 | 控制参数 |
|---|---|---|
| 实时上传 | 有新数据立即传 | `Realtime=1` |
| 间隔上传 | 按间隔时间检查并传送 | `TransInterval`（分钟） |
| 定时上传 | 按指定时间点传送 | `TransTimes`（如 `00:00;14:00`） |

> 若支持实时上传，则间隔/定时方式不起作用。

---

## 3. 初始化信息交互

设备首次连接或重连时发起，服务器返回配置参数。**此步骤成功后才能使用其他功能。**

### 3.1 客户端请求

```
GET /iclock/cdata?SN=${SerialNumber}&options=all&pushver=${XXX}&DeviceType=${XXX}&language=${XXX}&pushcommkey=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
```

**请求参数：**

| 参数 | 必选 | 说明 |
|---|---|---|
| `SN` | 是 | 设备序列号 |
| `options` | 是 | 固定值 `all`，表示获取服务器配置参数 |
| `pushver` | 否 | 设备当前 push 协议版本，新开发客户端必须 ≥ 2.2.14（见附录6） |
| `DeviceType` | 否 | 子协议类型：`att`（标准考勤）/ `pid`（人证）/ `ins`（信息屏） |
| `language` | 否 | 设备支持的语言编号（见附录2） |
| `pushcommkey` | 否 | 设备与服务器绑定的密文信息，用于授权判断 |

### 3.2 服务器响应

```
HTTP/1.1 200 OK
Date: ${XXX}
Content-Length: ${XXX}

GET OPTION FROM: ${SerialNumber}
${XXX}Stamp=${XXX}
ErrorDelay=${XXX}
Delay=${XXX}
TransTimes=${XXX}
TransInterval=${XXX}
TransFlag=${XXX}
TimeZone=${XXX}
Realtime=${XXX}
Encrypt=${XXX}
ServerVer=${XXX}
PushProtVer=${XXX}
PushOptionsFlag=${XXX}
PushOptions=${XXX}
```

**响应参数说明：**

| 参数 | 说明 | 备注 |
|---|---|---|
| `GET OPTION FROM:` | 响应第1行，格式为 `GET OPTION FROM: ${SN}` | 使用 LF 间隔后续配置 |
| `${XXX}Stamp` | 各数据类型的时间戳标记 | 支持 ATTLOG / OPERLOG / ATTPHOTO / BIODATA / IDCARD / ERRORLOG |
| `ErrorDelay` | 联网失败后重连间隔（秒） | 建议 30~300 |
| `Delay` | 正常联网时请求间隔（秒） | 建议 2~60，即获取命令的间隔 |
| `TransTimes` | 定时上传时间点 | 格式 `时:分`，多个用分号分开，最多10个，如 `00:00;14:00` |
| `TransInterval` | 间隔上传周期（分钟） | 0=不检查 |
| `TransFlag` | 自动上传数据类型标识 | 见下方详细说明 |
| `TimeZone` | 服务器时区 | 整时区用小时（如 `8`），半时区/1/4时区用分钟（如 `330` 表示东5半区） |
| `Realtime` | 是否实时传送 | 1=实时，0=定时/间隔 |
| `Encrypt` | 是否加密传送 | 1=加密 |
| `EncryptFlag` | 数据加密标识 | 如 `10000000`，第1位=考勤记录（仅 2.3.0+ 支持，使用 rc4） |
| `ServerVer` | 服务器协议版本 | 新开发必须 ≥ 2.2.14 |
| `PushProtVer` | 服务端协议版本号 | 见附录6 |
| `PushOptionsFlag` | 是否支持设备推送配置参数 | 0=不支持，1=支持 |
| `PushOptions` | 需要设备推送的参数列表 | 如 `FingerFunOn,FaceFunOn` |
| `ATTPHOTOBase64` | 考勤照片是否 base64 编码 | 1=base64 |
| `MultiBioDataSupport` | 支持多模态生物特征模板 | type 按位定义，冒号隔开，如 `0:1:1:0:0:0:0:0:0:0` |
| `MultiBioPhotoSupport` | 支持多模态生物特征图片 | 同上格式 |
| `IRTempUnitTrans` | 温度上传单位 | 0=摄氏度，1=华氏度（影响 ATTLOG 的 ConvTemperature 字段） |
| `QRCodeDecryptType` | 二维码解密方式 | 1=AES256(固定密钥)，2=AES256(随机密钥)，3=RSA1024 |
| `QRCodeDecryptKey` | 二维码密钥 | |
| `SupportPing` | 服务器是否支持 ping 协议 | 用于心跳保持 |

### 3.3 TransFlag 详解

**格式一（位标记）：** `TransFlag=1111000000...`

| 第几位 | 数据类型 |
|---|---|
| 1 | 考勤记录 |
| 2 | 操作日志 |
| 3 | 考勤照片 |
| 4 | 登记新指纹 |
| 5 | 登记新用户 |
| 6 | 指纹图片 |
| 7 | 修改用户信息 |
| 8 | 修改指纹 |
| 9 | 新登记人脸 |
| 10 | 用户照片 |
| 11 | 工作号码 |
| 12 | 比对照片 |

> 当全部为 0（`TransFlag=0000000000`）时，表示仅支持上传考勤照片。

**格式二（字符串标记）：** `TransFlag=TransData AttLog\tOpLog\tAttPhoto...`

| 字符串 | 数据类型 |
|---|---|
| `AttLog` | 考勤记录 |
| `OpLog` | 操作日志 |
| `AttPhoto` | 考勤照片 |
| `EnrollUser` | 登记新用户 |
| `ChgUser` | 修改用户信息 |
| `EnrollFP` | 登记新指纹 |
| `ChgFP` | 修改指纹 |
| `FPImag` | 指纹图片 |
| `FACE` | 新登记人脸 |
| `UserPic` | 用户照片 |
| `WORKCODE` | 工作号码 |
| `BioPhoto` | 比对照片 |

> **开发建议：** 客户端同时支持两种格式；服务端支持格式二即可。

### 3.4 时间戳标记说明

| 数据类型 | Stamp 参数 | 说明 |
|---|---|---|
| 考勤记录 | `ATTLOGStamp` | 断点续传标记 |
| 操作日志 | `OPERLOGStamp` | 断点续传标记 |
| 考勤照片 | `ATTPHOTOStamp` | 断点续传标记 |
| 一体化模板 | `BIODATAStamp` | 断点续传标记 |
| 身份证信息 | `IDCARDStamp` | 断点续传标记 |
| 异常日志 | `ERRORLOGStamp` | 断点续传标记 |

> **注意：** 时间戳存在缺陷——修改时间会导致设备无法正确判断已上传数据。新架构固件已废弃时间戳，仅为兼容老服务器保留。服务器将时间戳置 0 时，设备重新上传对应数据。

### 3.5 请求/响应示例

```
# 客户端请求
GET /iclock/cdata?SN=0316144680030&options=all&pushver=2.2.14&language=83&pushcommkey=4a9594af164f2b9779b59e8554b5df26 HTTP/1.1
Host: 58.250.50.81:8011
User-Agent: iClock Proxy/1.09
Connection: close
Accept: */*

# 服务器响应
HTTP/1.1 200 OK
Server: nginx/1.6.0
Date: Fri, 03 Jul 2015 06:53:01 GMT
Content-Type: text/plain
Content-Length: 190

GET OPTION FROM: 0316144680030
ATTLOGStamp=None
OPERLOGStamp=9999
ATTPHOTOStamp=None
ErrorDelay=30
Delay=10
TransTimes=00:00;14:05
TransInterval=1
TransFlag=TransData AttLog	OpLog	AttPhoto	EnrollUser	ChgUser	EnrollFP	ChgFP	UserPic
TimeZone=8
Realtime=1
Encrypt=None
```

---

## 4. 交换公钥（通信加密）

> 仅在支持通信加密的场合使用（push 协议版本 ≥ 2.4.0）。

设备推送设备公钥，接收服务器返回的服务器公钥。

```
POST /iclock/exchange?SN=${SerialNumber}&type=publickey HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

PublicKey=${XXX}
```

**服务器响应：**

```
HTTP/1.1 200 OK
Set-Cookie: ${XXX}; Path=/; HttpOnly
Content-Type: application/push;charset=UTF-8

PublicKey=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PublicKey`（请求） | 设备公钥 |
| `PublicKey`（响应） | 服务器公钥 |

---

## 5. 交换因子（通信加密）

> 仅在支持通信加密的场合使用（push 协议版本 ≥ 2.4.0）。

设备推送设备因子，接收服务器返回的服务器因子。

```
POST /iclock/exchange?SN=${SerialNumber}&type=factors HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

Factors=${XXX}
```

**服务器响应：**

```
HTTP/1.1 200 OK
Content-Type: application/push;charset=UTF-8

Factors=${XXX}
```

---

## 6. 推送配置信息

设备主动推送相关配置信息（功能开关等），当配置变化时主动推送。

```
POST /iclock/cdata?SN=${SerialNumber}&table=options HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${key}=${Value},${key}=${Value},......,${key}=${Value}
```

**推送的配置参数：**

| 参数 | 说明 |
|---|---|
| `FingerFunOn` | 指纹功能开关 |
| `FaceFunOn` | 人脸功能开关 |
| `UserPicURLFunOn` | 用户照片是否使用 URL 方式下发 |
| `MultiBioDataSupport` | 支持多模态生物特征模板（type 按位定义，冒号隔开） |
| `MultiBioPhotoSupport` | 支持多模态生物特征图片 |
| `MultiBioVersion` | 多模态生物特征数据版本（如 `0:10.0:7.0:0:0:0:0:0:0:0`） |
| `MultiBioDataCount` | 当前模板数量 |
| `MultiBioPhotoCount` | 当前照片数量 |
| `MaxMultiBioDataCount` | 模板最大容量 |
| `MaxMultiBioPhotoCount` | 照片最大容量 |
| `SubcontractingUpgradeFunOn` | 分包升级功能开关 |
| `IRTempDetectionFunOn` | 红外温度检测功能 |
| `MaskDetectionFunOn` | 口罩检测功能 |
| `IsSupportQRcode` | 是否支持二维码（0/1） |
| `QRCodeEnable` | 是否开启二维码功能（0/1） |
| `QRCodeDecryptFunList` | 二维码解密功能支持（位标记，如 `101` 表示支持方案一和三） |

**服务器响应：**

```
HTTP/1.1 200 OK
Content-Length: 2

OK
```

**示例：**

```
# 客户端请求
POST /iclock/cdata?SN=0316144680030&table=options HTTP/1.1
Host: 58.250.50.81:8011
Content-Length: 26

FingerFunOn=1,FaceFunOn=1,UserPicURLFunOn=1

# 服务器响应
HTTP/1.1 200 OK
Content-Length: 2

OK
```

---

## 7. 上传更新信息

复用**获取命令**请求，在 URL 上加入 `INFO` 参数，上传设备状态信息。

```
GET /iclock/getrequest?SN=${SerialNumber}&INFO=${Value1},${Value2},......,${Value13} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
```

**INFO 参数说明：**

| 位置 | 参数 | 说明 |
|---|---|---|
| Value1 | 固件版本号 | 如 `Ver 2.0.12-20150625` |
| Value2 | 登记用户数 | |
| Value3 | 登记指纹数 | |
| Value4 | 考勤记录数 | |
| Value5 | 设备 IP 地址 | |
| Value6 | 指纹算法版本 | |
| Value7 | 人脸算法版本 | |
| Value8 | 注册人脸所需人脸个数 | |
| Value9 | 登记人脸数 | |
| Value10 | 设备支持功能标示 | 格式 `101`，位标记（见下表） |
| Value11 | 登记卡数量 | |
| Value12 | 登记用户照片数量 | |
| Value13 | 考勤照片数量 | |

**Value10 功能标示位：**

| 第几位 | 功能描述 |
|---|---|
| 1 | 指纹功能 |
| 2 | 人脸功能 |
| 3 | 用户照片功能 |
| 4 | 比对照片功能（BioPhotoFun 需设为 1） |
| 5 | 可见光人脸模板功能（BioDataFun 需设为 1，需 VisilightFun=1 时才推送） |

> 默认推送前3位，需设置 `VisilightFun=1` 时才推送5位。

**示例：**

```
GET /iclock/getrequest?SN=0316144680030&INFO=Ver%202.0.12-20150625,0,0,0,192.168.16.27,10,7,15,0,111 HTTP/1.1
Host: 58.250.50.81:8011
```

---

## 8. 心跳

用于与服务器保持心跳。当处理大数据上传时用 ping 保持心跳，大数据处理完用 getrequest 保持心跳。

```
GET /iclock/ping?SN=${SerialNumber} HTTP/1.1
Cookie: token=${XXX}
Host: ${ServerIP}:${ServerPort}
```

**服务器响应：**

```
HTTP/1.1 200 OK
Content-Length: 2

OK
```

**示例：**

```
GET /iclock/ping?SN=3383154200002 HTTP/1.1
Cookie: token=cb386eb5f8219329db63356fb262ddff
Host: 192.168.213.17:8088
User-Agent: iClock Proxy/1.09
Connection: starting
Accept: application/push
Accept-Charset: UTF-8
```

---

## 9. 上传数据

具体哪些数据自动上传由服务器控制（见初始化的 `TransFlag` 参数）。

### 9.1 上传考勤记录

```
POST /iclock/cdata?SN=${SerialNumber}&table=ATTLOG&Stamp=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${DataRecord}
```

**数据格式（Tab 分隔）：**

```
${Pin}\t${Time}\t${Status}\t${Verify}\t${Workcode}\t${Reserved1}\t${Reserved2}\tMaskFlag\tTemperature\tConvTemperature\t${TimeOffset}\t${ExtendData}
```

| 字段 | 说明 | 格式/取值 |
|---|---|---|
| `Pin` | 用户工号 | |
| `Time` | 验证时间 | `YYYY-MM-DD HH:MM:SS` |
| `Status` | 考勤状态 | |
| `Verify` | 验证方式 | 见附录7 |
| `Workcode` | 工作代码 | |
| `Reserved1` | 保留字段1 | |
| `Reserved2` | 保留字段2 | |
| `MaskFlag` | 是否戴口罩 | 0 或 1 |
| `Temperature` | 温度 | 带小数点，如 `36.2` |
| `ConvTemperature` | 转换后温度 | 受 `IRTempUnitTrans` 参数控制单位 |
| `TimeOffset` | UTC 时间偏移（秒） | 如 `+28800` 或 `-28800`，空值=无偏移 |
| `ExtendData` | 扩展字段（Base64 编码的 JSON） | 目前包含 GPS 信息 |

**ExtendData 中 GPS 信息格式（原生 JSON）：**

```json
{
  "GPSInfo": {
    "longitude": "114.080021",
    "latitude": "22.763456"
  }
}
```

> 不支持 GPS 时，经纬度值为 `-1`。上传时 JSON 转为 Base64 格式。

**服务器响应：**

```
HTTP/1.1 200 OK
Content-Length: ${XXX}

OK:${XXX}
```

> `${XXX}` 为成功处理的记录条数。多条记录之间使用 LF 连接。

### 9.2 上传考勤照片

```
POST /iclock/cdata?SN=${SerialNumber}&table=ATTPHOTO&Stamp=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${DataRecord}
```

**数据格式：**

```
PIN=${XXX}\nSN=${SerialNumber}\nsize=${XXX}\nCMD=uploadphoto\0${BinaryData}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 考勤照片文件名（目前只支持 jpg 格式） |
| `SN` | 客户端序列号 |
| `size` | 考勤照片原始大小 |
| `${BinaryData}` | 原始图片二进制数据流 |

> 考勤照片**不支持**多条记录传输。

**服务器响应：** `OK`

### 9.3 上传操作记录

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${DataRecord}
```

**数据格式（Tab 分隔）：**

```
OPLOG ${OpType}\t${Operator}\t${OpTime}\t${OpWho}\t${Value1}\t${Value2}\t${Value3}
```

| 字段 | 说明 | 参考 |
|---|---|---|
| `OpType` | 操作代码 | 见附录3 |
| `Operator` | 操作者 | |
| `OpTime` | 操作时间 | `YYYY-MM-DD HH:MM:SS` |
| `OpWho` | 操作对象1 | 见附录4 |
| `Value1` | 操作对象2 | 见附录4 |
| `Value2` | 操作对象3 | 见附录4 |
| `Value3` | 操作对象4 | 见附录4 |

**服务器响应：** `OK:${XXX}`（成功处理的记录条数）

### 9.4 上传用户信息

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${DataRecord}
```

**数据格式（Tab 分隔）：**

```
USER PIN=${XXX}\tName=${XXX}\tPri=${XXX}\tPasswd=${XXX}\tCard=${XXX}\tGrp=${XXX}\tTZ=${XXX}\tVerify=${XXX}\tViceCard=${XXX}
```

| 字段 | 说明 | 备注 |
|---|---|---|
| `PIN` | 用户工号 | |
| `Name` | 用户姓名 | 中文设备用 GB2312，其他用 UTF-8 |
| `Pri` | 用户权限 | 0=普通, 2=登记员, 6=管理员, 10=自定义, 14=超级管理员 |
| `Passwd` | 密码 | |
| `Card` | 卡号（主卡） | 支持十六进制 `[%02x%02x%02x%02x]` 或字符串格式 |
| `Grp` | 用户所属组 | 默认 1 |
| `TZ` | 时间段编号 | 16位字符串，每4位一段（组时间段/个人时间段1/2/3） |
| `Verify` | 验证方式 | 见附录7；空或 -1=使用组验证方式 |
| `ViceCard` | 副卡号 | 字符串格式 |

**TZ 字段格式说明：**

```
0000000000000000  → 使用组时间段
0001000200000000  → 个人时间段1=编号2
0001000200010000  → 个人时间段1=编号2, 个人时间段2=编号1
```

**服务器响应：** `OK:${XXX}`

### 9.5 上传身份证信息（仅人证协议）

> 需要 PushProtVer ≥ 2.3.0

```
POST /iclock/cdata?SN=${SerialNumber}&table=IDCARD&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
IDCARD PIN=${XXX}\tSNNum=${XXX}\tIDNum=${XXX}\tDNNum=${XXX}\tName=${XXX}\tGender=${XXX}\tNation=${XXX}\tBirthday=${XXX}\tValidInfo=${XXX}\tAddress=${XXX}\tAdditionalInfo=${XXX}\tIssuer=${XXX}\tPhoto=${XXX}\tFPTemplate1=${XXX}\tFPTemplate2=${XXX}\tReserve=${XXX}\tNotice=${XXX}
```

| 字段 | 说明 | 格式 |
|---|---|---|
| `PIN` | 用户工号 | 未绑定身份证时为 0 |
| `SNNum` | 身份证物理卡号 | |
| `IDNum` | 公民身份证号码 | |
| `DNNum` | 居民身份证证卡序列号（卡体管理号） | |
| `Name` | 姓名 | UTF-8 |
| `Gender` | 性别代码 | 1=男, 2=女 |
| `Nation` | 民族代码 | 见下方民族代码表 |
| `Birthday` | 出生日期 | `yyyyMMdd` |
| `ValidInfo` | 有效期 | `yyyyMMddyyyyMMdd`（开始+结束） |
| `Address` | 地址 | UTF-8 |
| `AdditionalInfo` | 机读追加地址 | UTF-8 |
| `Issuer` | 签发机关 | UTF-8 |
| `Photo` | 身份证照片 | 加密数据，Base64 传输 |
| `FPTemplate1` | 指纹1特征数据 | Base64 |
| `FPTemplate2` | 指纹2特征数据 | Base64 |
| `Reserve` | 保留字段 | |
| `Notice` | 备注 | UTF-8 |

**民族代码（部分常用）：**

| 代码 | 民族 | 代码 | 民族 | 代码 | 民族 |
|---|---|---|---|---|---|
| 0 | 解码错 | 1 | 汉 | 2 | 蒙古 |
| 3 | 回 | 4 | 藏 | 5 | 维吾尔 |
| 6 | 苗 | 7 | 彝 | 8 | 壮 |
| 9 | 布依 | 10 | 朝鲜 | 11 | 满 |
| 12 | 侗 | 13 | 瑶 | 14 | 白 |
| 15 | 土家 | 16 | 哈尼 | 17 | 哈萨克 |
| ... | ... | 56 | 基诺 | 57 | 编码错 |
| 97 | 其它 | 98 | 外国血统 | | |

> 完整民族代码表参见 PDF 附录，代码 0-56 对应 56 个民族，57=编码错，97=其它，98=外国血统。

### 9.6 上传身份证考勤记录（仅人证协议）

> 需要 PushProtVer ≥ 2.4.0

```
POST /iclock/cdata?SN=${SerialNumber}&table=ATTLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
${Pin}\t${Time}\t${Status}\t${Verify}\t${Workcode}\t${Reserved1}\t${Reserved2}\t${IDNum}\t${Type}
```

| 字段 | 说明 |
|---|---|
| `IDNum` | 身份证号 |
| `Type` | 记录类型：0=考勤，1=核验 |

**Type=1（核验）时的字段说明：**

| 字段 | 取值 |
|---|---|
| `Status` | 0=成功, 1=失败, 2=黑名单 |
| `Verify` | 1=人脸, 2=人脸+指纹, 3=指纹+人脸 |

### 9.7 上传身份证考勤照片（仅人证协议）

> 需要 PushProtVer ≥ 2.4.0

**数据格式：**

```
PIN=${时间-照片类型-工号-身份证号}.jpg\nSN=${SerialNumber}\nsize=${XXX}\nCMD=uploadphoto\0${BinaryData}
```

**照片类型：**

| 值 | 说明 |
|---|---|
| 0 | 用户考勤成功照片 |
| 1 | 用户考勤失败照片 |
| 2 | 黑名单照片 |
| 3 | 人证核验成功照片 |
| 4 | 人证核验失败照片 |

### 9.8 上传指纹模板

> 需要 PushProtVer ≥ 2.2.14，支持的指纹算法版本 ≤ 10.0

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
FP PIN=${XXX}\tFID=${XXX}\tSize=${XXX}\tValid=${XXX}\tTMP=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 用户工号 |
| `FID` | 手指编号（0-9） |
| `Size` | 指纹模版 Base64 编码后的长度 |
| `Valid` | 0=无效, 1=正常, 3=胁迫 |
| `TMP` | Base64 编码的指纹模版数据 |

### 9.9 上传面部模板

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
FACE PIN=${XXX}\tFID=${XXX}\tValid=${XXX}\tSize=${XXX}\tTMP=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 用户工号 |
| `FID` | 面部模版编号（从 0 开始） |
| `Valid` | 0=无效, 1=正常 |
| `Size` | 面部模版 Base64 编码后的长度 |
| `TMP` | Base64 编码的面部模版数据 |

### 9.10 上传指静脉模板

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
FVEIN Pin=${XXX}\tFID=${XXX}\tIndex=${XXX}\tValid=${XXX}\tSize=${XXX}\tTmp=${XXX}
```

| 字段 | 说明 |
|---|---|
| `Pin` | 用户工号 |
| `FID` | 手指编号（0-9） |
| `Index` | 同一手指的指静脉模板编号（0-2） |
| `Valid` | 0=无效, 1=正常 |
| `Size` | Base64 编码后的长度 |
| `Tmp` | Base64 编码的指静脉模版数据 |

### 9.11 上传一体化模板

> 后续新增的生物识别模板统一使用此格式，通过 Type 区分类型。

```
POST /iclock/cdata?SN=${SerialNumber}&table=BIODATA&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
BIODATA Pin=${XXX}\tNo=${XXX}\tIndex=${XXX}\tValid=${XXX}\tDuress=${XXX}\tType=${XXX}\tMajorVer=${XXX}\tMinorVer=${XXX}\tFormat=${XXX}\tTmp=${XXX}
```

| 字段 | 说明 | 取值 |
|---|---|---|
| `Pin` | 用户工号 | |
| `No` | 生物具体个体编号 | 指纹/指静脉：0-9；面部：0；虹膜：0左1右；掌静脉/可见光手掌：0左1右 |
| `Index` | 个体图片编号 | 从 0 开始 |
| `Valid` | 0=无效, 1=正常 | |
| `Duress` | 0=非胁迫, 1=胁迫 | |
| `Type` | 生物识别类型 | 见下表 |
| `MajorVer` | 算法主版本号 | |
| `MinorVer` | 算法次版本号 | |
| `Format` | 模板格式 | 见下表 |
| `Tmp` | Base64 编码的模板数据 | |

**Type 生物识别类型：**

| 值 | 类型 | 归属 |
|---|---|---|
| 0 | 通用 | — |
| 1 | 指纹 | 近红外 |
| 2 | 近红外人脸 | 近红外 |
| 3 | 声纹 | 近红外 |
| 4 | 虹膜 | 近红外 |
| 5 | 视网膜 | 近红外 |
| 6 | 掌纹 | 近红外 |
| 7 | 指静脉 | 近红外 |
| 8 | 掌静脉 | 近红外 |
| 9 | 可见光人脸 | 可见光 |
| 10 | 可见光手掌 | 可见光 |

**各类型支持的算法版本：**

| 类型 | 算法版本 |
|---|---|
| 指纹 | 9.0、10.3、12.0 |
| 指静脉 | 3.0 |
| 面部 | 5.0、7.0、8.0 |
| 掌静脉 | 1.0 |
| 可见光面部 | 58.0、38.0 |
| 可见光手掌 | 32.2 |

**Format 模板格式：**

| 类型 | 值 | 格式 |
|---|---|---|
| 指纹 | 0 | ZK |
| 指纹 | 1 | ISO |
| 指纹 | 2 | ANSI |
| 指静脉 | 0 | ZK |
| 面部 | 0 | ZK |
| 掌静脉 | 0 | ZK |
| 可见光手掌 | 0 | ZK |

### 9.12 上传用户照片

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
USERPIC PIN=${XXX}\tFileName=${XXX}\tSize=${XXX}\tContent=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 用户工号 |
| `FileName` | 用户照片文件名（目前只支持 jpg 格式） |
| `Size` | 用户照片 Base64 编码后的长度 |
| `Content` | Base64 编码的用户照片数据 |

### 9.13 上传数据包

> 将多种数据打包上传（tgz 格式）。

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&ContentType=tgz HTTP/1.1
```

**请求实体：** 打包后的数据（内部格式同各数据类型的上传格式），多条记录间用 LF 连接，然后打包为 tgz。

### 9.14 上传比对照片（仅可见光设备）

> 需要 PushProtVer ≥ 2.2.14

```
POST /iclock/cdata?SN=${SerialNumber}&table=OPERLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
BIOPHOTO PIN=${XXX}\tFileName=${XXX}\tType=${XXX}\tNo=${XXX}\tIndex=${XXX}\tSize=${XXX}\tContent=${XXX}
```

| 字段 | 说明 | 取值 |
|---|---|---|
| `PIN` | 用户工号 | |
| `FileName` | 图片文件名（jpg 格式） | |
| `Type` | 生物识别类型 | 0=通用, 1=指纹, 2=面部(近红外), 3=声纹, 4=虹膜, 5=视网膜, 6=掌纹, 7=指静脉, 8=手掌, 9=可见光人脸, 10=可见光手掌 |
| `No` | 生物个体编号 | 默认 0（见一体化模板的 No 说明） |
| `Index` | 个体图片编号 | 从 0 开始 |
| `Size` | Base64 编码后的长度 | |
| `Content` | Base64 编码的图片数据 | |

### 9.15 上传异常日志

> 需要 PushProtVer ≥ 2.4.1

```
POST /iclock/cdata?SN=${SerialNumber}&table=ERRORLOG&Stamp=${XXX} HTTP/1.1
```

**数据格式（Tab 分隔）：**

```
ERRORLOG ErrCode=${XXX}\tErrMsg=${XXX}\tDataOrigin=${XXX}\tCmdId=${XXX}\tAdditional=${XXX}
```

| 字段 | 说明 |
|---|---|
| `ErrCode` | 错误编码（见附录9） |
| `ErrMsg` | 错误消息 |
| `DataOrigin` | 数据源：`dev`=设备源, `cmd`=软件下发数据 |
| `CmdId` | 软件下发命令号 |
| `Additional` | 附加信息（Base64，原生 JSON） |

---

## 10. 获取命令

服务器通过设备轮询 `/iclock/getrequest` 下发命令。

### 10.0 命令格式

```
GET /iclock/getrequest?SN=${SerialNumber} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
```

**服务器响应：**
- 无命令时返回 `OK`
- 有命令时返回命令记录

**命令记录格式：**

```
C:${CmdID}:${CmdDesc} ${XXX}
```

| 字段 | 说明 |
|---|---|
| `CmdID` | 命令编号（服务器随机生成，支持数字+字母，长度 ≤ 16） |
| `CmdDesc` | 命令描述：`DATA`（数据命令）或各种控制命令描述 |

> 多条命令之间使用 LF 连接。

### 10.1 DATA UPDATE 子命令

命令格式：`C:${CmdID}:DATA UPDATE ${TableName} ${DataRecord}`

#### 10.1.1 用户信息

```
C:${CmdID}:DATA UPDATE USERINFO PIN=${XXX}\tName=${XXX}\tPri=${XXX}\tPasswd=${XXX}\tCard=${XXX}\tGrp=${XXX}\tTZ=${XXX}\tVerify=${XXX}\tViceCard=${XXX}\tStartDatetime=${XXX}\tEndDatetime=${XXX}\tExpires=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 用户工号 |
| `Name` | 用户姓名（中文设备用 GB2312，其他用 UTF-8） |
| `Pri` | 权限：0=普通, 2=登记员, 6=管理员, 10=自定义, 14=超级管理员 |
| `Passwd` | 密码 |
| `Card` | 卡号（十六进制 `[%02x%02x%02x%02x]` 或字符串） |
| `Grp` | 用户组（默认 1） |
| `TZ` | 时间段编号（16位字符串） |
| `Verify` | 验证方式（见附录7，空/-1=使用组验证方式） |
| `ViceCard` | 副卡号 |
| `StartDatetime` | 有效期开始（`YYYY-MM-DDTHH:MM:SS`） |
| `EndDatetime` | 有效期结束（`YYYY-MM-DDTHH:MM:SS`） |
| `Expires` | 是否启用有效期（1=启用，0=不启用） |

> **注意：** 启用有效期需设备参数 `UserValidTimeFun=1`。

**人证协议附加字段：** `Phone`、`Gender`、`Nation`、`IDNum`

#### 10.1.2 身份证信息（仅人证协议）

```
C:${CmdID}:DATA UPDATE IDCARD PIN=${XXX}\tSNNum=${XXX}\tIDNum=${XXX}\tDNNum=${XXX}\tName=${XXX}\tGender=${XXX}\tNation=${XXX}\tBirthday=${XXX}\tValidInfo=${XXX}\tAddress=${XXX}\tAdditionalInfo=${XXX}\tIssuer=${XXX}\tPhoto=${XXX}\tFPTemplate1=${XXX}\tFPTemplate2=${XXX}\tReserve=${XXX}\tNotice=${XXX}
```

> 字段说明同 [9.5 上传身份证信息](#95-上传身份证信息仅人证协议)。

#### 10.1.3 指纹模板

```
C:${CmdID}:DATA UPDATE FINGERTMP PIN=${XXX}\tFID=${XXX}\tSize=${XXX}\tValid=${XXX}\tTMP=${XXX}
```

| 字段 | 说明 |
|---|---|
| `PIN` | 用户工号 |
| `FID` | 手指编号（0-9） |
| `Size` | Base64 编码后的长度 |
| `Valid` | 0=无效, 1=正常, 3=胁迫 |
| `TMP` | Base64 编码的指纹模版 |

> **注意：** 支持的指纹算法版本 ≤ 10.0。

#### 10.1.4 面部模板

```
C:${CmdID}:DATA UPDATE FACE PIN=${XXX}\tFID=${XXX}\tValid=${XXX}\tSize=${XXX}\tTMP=${XXX}
```

#### 10.1.5 指静脉模板

```
C:${CmdID}:DATA UPDATE FVEIN Pin=${XXX}\tFID=${XXX}\tIndex=${XXX}\tValid=${XXX}\tSize=${XXX}\tTmp=${XXX}
```

#### 10.1.6 一体化模板

```
C:${CmdID}:DATA UPDATE BIODATA Pin=${XXX}\tNo=${XXX}\tIndex=${XXX}\tValid=${XXX}\tDuress=${XXX}\tType=${XXX}\tMajorVer=${XXX}\tMinorVer=${XXX}\tFormat=${XXX}\tTmp=${XXX}
```

> 字段说明同 [9.11 上传一体化模板](#911-上传一体化模板)。

#### 10.1.7 用户照片

```
C:${CmdID}:DATA UPDATE USERPIC PIN=${XXX}\tFormat=${XXX}\tUrl=${XXX}\tSize=${XXX}\tContent=${XXX}
```

| 字段 | 说明 |
|---|---|
| `Format` | 下发方式：0=base64, 1=url（默认 0） |
| `Url` | Format=1 时的服务器文件地址 |
| `Size` | Format=0 时 Base64 编码后的长度 |
| `Content` | Format=0 时 Base64 编码的用户照片 |

#### 10.1.8 比对照片（仅可见光设备）

```
C:${CmdID}:DATA UPDATE BIOPHOTO PIN=${XXX}\tType=${XXX}\tNo=${XXX}\tIndex=${XXX}\tSize=${XXX}\tContent=${XXX}\tFormat=${XXX}\tUrl=${XXX}\tPostBackTmpFlag=${XXX}
```

| 字段 | 说明 |
|---|---|
| `Format` | 下发方式：0=base64, 1=url |
| `Url` | 服务器文件地址（相对路径直接发相对路径） |
| `PostBackTmpFlag` | 是否回传模版：0=不需要, 1=需要（默认不回传） |

#### 10.1.9 短消息

```
C:${CmdID}:DATA UPDATE SMS MSG=${XXX}\tTAG=${XXX}\tUID=${XXX}\tMIN=${XXX}\tStartTime=${XXX}
```

| 字段 | 说明 |
|---|---|
| `MSG` | 短消息内容（最大 320 字节，中文用 GB2312） |
| `TAG` | 类型：253=公共, 254=用户, 255=预留 |
| `UID` | 短消息编号（整数） |
| `MIN` | 有效时长（分钟） |
| `StartTime` | 生效开始时间（`YYYY-MM-DD HH:MM:SS`） |

#### 10.1.10 个人短消息用户列表

```
C:${CmdID}:DATA UPDATE USER_SMS PIN=${XXX}\tUID=${XXX}
```

#### 10.1.11 宣传照片

```
C:${CmdID}:DATA UPDATE ADPIC Index=${XXX}\tSize=${XXX}\tExtension=${XXX}\tContent=${XXX}
```

#### 10.1.12 工作代码

```
C:${CmdID}:DATA UPDATE WORKCODE PIN=${XXX}\tCODE=${XXX}\tNAME=${XXX}
```

#### 10.1.13 快捷键

```
C:${CmdID}:DATA UPDATE ShortcutKey KeyID=${XXX}\tKeyFun=${XXX}\tStatusCode=${XXX}\tShowName=${XXX}\tAutoState=${XXX}\tAutoTime=${XXX}\tSun=${XXX}\tMon=${XXX}\tTue=${XXX}\tWed=${XXX}\tThu=${XXX}\tFri=${XXX}\tSat=${XXX}
```

| 字段 | 说明 |
|---|---|
| `KeyID` | 快捷键 ID：1=F1, 2=F2, ... 8=F8 |
| `KeyFun` | 功能：0=未定义, 1=状态键, 2=工作号码, 3=短消息, 4=按键求助, 5=查询考勤记录, 6=查询最后考勤记录 |
| `StatusCode` | 考勤状态 |
| `ShowName` | 状态名称 |
| `AutoState` | 自动切换 |
| `AutoTime` | 周一到周日自动切换时间（如 `08:00;09:00;...;14:00`） |
| `Sun`~`Sat` | 周日到周六是否切换 |

#### 10.1.14 门禁组

```
C:${CmdID}:DATA UPDATE AccGroup ID=${XXX}\tVerify=${XXX}\tValidHoliday=${XXX}\tTZ=${XXX}
```

| 字段 | 说明 |
|---|---|
| `ID` | 门禁组编号 |
| `Verify` | 组验证方式（默认 0，见附录7） |
| `ValidHoliday` | 节假日是否有效（0-1） |
| `TZ` | 时间段，格式 `1;0;0`（时间段1;时间段2;时间段3） |

#### 10.1.15 门禁时间表

```
C:${CmdID}:DATA UPDATE AccTimeZone UID=${XXX}\tSunStart=${XXX}\tSunEnd=${XXX}\tMonStart=${XXX}\tMonEnd=${XXX}\tTuesStart=${XXX}\tTuesEnd=${XXX}\tWedStart=${XXX}\tWedEnd=${XXX}\tThursStart=${XXX}\tThursEnd=${XXX}\tFriStart=${XXX}\tFriEnd=${XXX}\tSatStart=${XXX}\tSatEnd=${XXX}
```

> 时间格式：`1159` 表示 11:59，`2359` 表示 23:59。

#### 10.1.16 门禁节假日

```
C:${CmdID}:DATA UPDATE AccHoliday UID=${XXX}\tHolidayName=${XXX}\tStartDate=${XXX}\tEndDate=${XXX}\tTimeZone=${XXX}
```

> 日期格式：`1123` 表示 11月23日。

#### 10.1.17 门禁多组验证

```
C:${CmdID}:DATA UPDATE AccUnLockComb UID=${XXX}\tGroup1=${XXX}\tGroup2=${XXX}\tGroup3=${XXX}\tGroup4=${XXX}\tGroup5=${XXX}
```

#### 10.1.18 身份证黑名单（仅人证协议）

```
C:${CmdID}:DATA UPDATE BLACKLIST IDNum=${XXX}\tName=${XXX}\tGender=${XXX}\tNation=${XXX}
```

#### 10.1.19 身份证白名单（仅人证协议）

```
C:${CmdID}:DATA UPDATE WHITELIST IDNum=${XXX}\tName=${XXX}\tGender=${XXX}\tNation=${XXX}\tStartDate=${XXX}\tEndDate=${XXX}
```

> 日期格式：`YYYY-MM-DD HH:MM:SS`

#### 10.1.20 设备壁纸照片

```
C:${CmdID}:DATA UPDATE WALLPAPER Index=${XXX}\tSize=${XXX}\tExtension=${XXX}\tContent=${XXX}
```

| 字段 | 说明 |
|---|---|
| `Index` | 图片索引（保存为 `wallpaper{Index}.{Extension}`） |
| `Size` | 原始图片大小（字节） |
| `Extension` | 扩展名：jpg / jpeg / png / gif / bmp |
| `Content` | Base64 编码 |

### 10.2 DATA DELETE 子命令

命令格式：`C:${CmdID}:DATA DELETE ${TableName} ${DataRecord}`

| 表名 | 删除条件 | 说明 |
|---|---|---|
| `USERINFO` | `PIN=${XXX}` | 删除用户（含指纹、面部、照片等） |
| `FINGERTMP` | `PIN=${XXX}` 或 `PIN=${XXX}\tFID=${XXX}` | 删除全部或指定手指指纹 |
| `FACE` | `PIN=${XXX}` | 删除面部模版 |
| `FVEIN` | `Pin=${XXX}` 或 `Pin=${XXX}\tFID=${XXX}` | 删除全部或指定手指指静脉 |
| `BIODATA` | `Pin=${XXX}` 或 `Pin=${XXX}\tType=${XXX}` 或 `Pin=${XXX}\tType=${XXX}\tNo=${XXX}` | 删除一体化模版 |
| `USERPIC` | `PIN=${XXX}` | 删除用户照片 |
| `BIOPHOTO` | `PIN=${XXX}\tType=${XXX}` | 删除比对照片 |
| `SMS` | `UID=${XXX}` | 删除短消息 |
| `WORKCODE` | `CODE=${XXX}` | 删除工作代码 |
| `ADPIC` | `Index=${XXX}` | 删除宣传照片 |
| `BLACKLIST` | `IDNum=${XXX}` | 删除身份证黑名单 |
| `WHITELIST` | `IDNum=${XXX}` | 删除身份证白名单 |
| `WALLPAPER` | `Index=${XXX}` | 删除壁纸照片 |

### 10.3 DATA QUERY 子命令

命令格式：`C:${CmdID}:DATA QUERY ${TableName} ${DataRecord}`

| 表名 | 查询条件 | 说明 |
|---|---|---|
| `ATTLOG` | `StartTime=${XXX}\tEndTime=${XXX}` | 查询指定时间段考勤记录 |
| `ATTPHOTO` | `StartTime=${XXX}\tEndTime=${XXX}` | 查询指定时间段考勤照片 |
| `USERINFO` | `PIN=${XXX}` | 查询用户基本信息 |
| `FINGERTMP` | `PIN=${XXX}` 或 `PIN=${XXX}\tFID=${XXX}` | 查询全部或指定手指指纹 |
| `BIODATA` | `Type=${XXX}` 或 `Type=${XXX}\tPin=${XXX}` 或 `Type=${XXX}\tPin=${XXX}\tNo=${XXX}` | 查询一体化模版 |

> 时间格式：`YYYY-MM-DD HH:MM:SS`

### 10.4 CLEAR 命令

| 命令 | 格式 | 回复 CMD | 说明 |
|---|---|---|---|
| 清除考勤记录 | `C:${CmdID}:CLEAR LOG` | `CLEAR_LOG` | |
| 清除考勤照片 | `C:${CmdID}:CLEAR PHOTO` | `CLEAR_PHOTO` | |
| 清除全部数据 | `C:${CmdID}:CLEAR DATA` | `CLEAR_DATA` | |
| 清除一体化模板 | `C:${CmdID}:CLEAR BIODATA` | `CLEAR_BIODATA` | |
| 清除所有用户数据 | `C:${CmdID}:CLEAR ALL USERINFO` | `CLEAR ALL USERINFO` | 不含考勤记录 |

### 10.5 检查命令

| 命令 | 格式 | 说明 |
|---|---|---|
| 检查数据更新 | `C:${CmdID}:CHECK` | 设备重新读取配置并按时间戳重新上传数据（服务器将 Stamp 置 0） |
| 检查并传送新数据 | `C:${CmdID}:LOG` | 设备立即检查并上传新数据 |
| 考勤数据自动校对 | `C:${CmdID}:VERIFY SUM ATTLOG StartTime=${XXX}\tEndTime=${XXX}` | 服务器下发校对时间段，设备返回记录总数 |

**考勤校对回复格式：**

```
ID=${XXX}&Return=${XXX}&CMD=VERIFY SUM&StartTime=${XXX}&EndTime=${XXX}&AttlogSum=${XXX}
```

### 10.6 配置选项命令

| 命令 | 格式 | 回复 CMD | 说明 |
|---|---|---|---|
| 设置选项 | `C:${CmdID}:SET OPTION ${Key}=${Value}` | `SET OPTION` | 单一配置设置 |
| 刷新选项 | `C:${CmdID}:RELOAD OPTIONS` | `RELOAD OPTIONS` | 重新加载配置 |
| 获取信息 | `C:${CmdID}:INFO` | `INFO` + 键值对 | 获取设备配置信息 |

**INFO 回复格式：**

```
ID=${XXX}&Return=${XXX}&CMD=INFO\n${Key}=${Value}\n${Key}=${Value}......
```

### 10.7 文件命令

#### 10.7.1 取客户端文件

```
C:${CmdID}:GetFile ${FilePath}
```

**回复格式：**

```
ID=${XXX}\nSN=${SerialNumber}\nFILENAME=${XXX}\nCMD=GetFile\nReturn=${XXX}\nContent=${BinaryData}
```

> `Return` 为文件大小，`Content` 为文件二进制数据流。

#### 10.7.2 发送文件到客户端

**功能1：下载并保存文件**

```
C:${CmdID}:PutFile ${URL}\t${FilePath}
```

- URL 以 `http://` 开头时为完整地址，否则附加 `/iclock/` 前缀
- tgz 文件自动解压到 FilePath 指定目录（未指定则解压到 `/mnt/mtdblock`）
- 其他格式文件需指定完整保存路径

**功能2：同步/追加数据**

```
C:${CmdID}:PutFile ${URL}\t${FilePath}\tAction=${Value}\tTableName=${Value}\tRecordCount=${Value}
```

| Action 值 | 说明 | 附加参数 |
|---|---|---|
| `SyncData` | 舍弃设备原有数据，同步为文件中的数据 | `TableName`（USERINFO/FINGERTMP/FACE）, `RecordCount` |
| `AppendData` | 追加文件中的数据到设备 | 无 |

**回复格式：**

```
ID=${XXX}\nReturn=${XXX}\nCMD=PutFile
```

> `Return` 为文件大小。

### 10.8 远程登记命令

#### 10.8.1 登记用户指纹

```
C:${CmdID}:ENROLL_FP PIN=${XXX}\tFID=${XXX}\tRETRY=${XXX}\tOVERWRITE=${XXX}
```

| 参数 | 说明 |
|---|---|
| `PIN` | 登记的工号 |
| `FID` | 登记的指纹编号 |
| `RETRY` | 登记失败重试次数 |
| `OVERWRITE` | 0=不覆盖（已有则返回错误），1=覆盖 |

**回复 CMD：** `ENROLL_FP`

#### 10.8.2 登记卡号

```
C:${CmdID}:ENROLL_MF PIN=${XXX}\tRETRY=${XXX}
```

**返回值：**

| 值 | 说明 |
|---|---|
| 0 | 成功 |
| -1 | 参数错误 |
| -3 | 存取错误 |
| 4 | 登记失败重试次数 |
| 5 | 登记超时退出 |
| 6 | 按 Esc 退出 |

#### 10.8.3 登记人脸/掌纹（一体化模板）

```
C:${CmdID}:ENROLL_BIO TYPE=${XXX}\tPIN=${XXX}\tCardNo=${XXX}\tRETRY=${XXX}\tOVERWRITE=${XXX}
```

| 参数 | 说明 |
|---|---|
| `TYPE` | 生物识别类型（0=通用, 1=指纹, 2=面部, 3=语音, 4=虹膜, 5=视网膜, 6=掌纹, 7=指静脉, 8=掌静脉, 9=可见光面部, 10=可见光手掌） |
| `PIN` | 登记的工号 |
| `CardNo` | 登记的卡号 |
| `RETRY` | 重试次数 |
| `OVERWRITE` | 0=不覆盖, 1=覆盖 |

**回复 CMD：** `ENROLL_BIO`

### 10.9 控制命令

| 命令 | 格式 | 回复 CMD | 说明 |
|---|---|---|---|
| 重启设备 | `C:${CmdID}:REBOOT` | `REBOOT` | |
| 输出开门信号 | `C:${CmdID}:AC_UNLOCK` | `AC_UNLOCK` | 门禁设备 |
| 取消报警 | `C:${CmdID}:AC_UNALARM` | `AC_UNALARM` | 门禁设备 |

### 10.10 其他命令

#### 10.10.1 执行系统命令

```
C:${CmdID}:SHELL ${SystemCmd}
```

**回复格式：**

```
ID=${XXX}\nSN=${SerialNumber}\nReturn=${XXX}\nCMD=Shell\nFILENAME=shellout.txt\nContent=${XXX}
```

> `Return` 为系统命令返回值，`Content` 为输出内容。

#### 10.10.2 在线升级

支持三种方式：

**方式一（服务器转格式）：**

```
C:${CmdID}:UPGRADE checksum=${XXX},url=${URL},size=${XXX}
```

> 固件文件由服务器转为 Base64 格式下发，设备接收后转为二进制并命名为 `emfw.cfg`。

**方式二（直接获取文件）：**

```
C:${CmdID}:UPGRADE type=1,checksum=${XXX},size=${XXX},url=${URL}
```

> 客户端直接获取固件升级文件，无需转格式。

**方式三（分包拉取）：**

```
C:${CmdID}:UPGRADE checksum=${XXX},size=${XXX},url=${URL},supportsubcontracting=${XXX}
```

> 使用 HTTP Range 协议分包拉取，设备默认每次拉取 1MB。`supportsubcontracting`：0=不支持, 1=支持。

**设备下载升级包：**

```
GET /iclock/file?SN=${SerialNumber}&url=${URL} HTTP/1.1
Cookie: token=${XXX}
```

**回复格式：** `ID=${CmdID}&Return=${XXX}&CMD=UPGRADE`

#### 10.10.3 后台验证

应用场景：设备验证成功后将人员编号上传到后端系统，后端系统返回是否允许通过。

```
POST /iclock/cdata?SN=${SerialNumber}&type=PostVerifyData HTTP/1.1
Host: ${ServerIP}:${ServerPort}

${PostData}
```

**服务器响应：** `OK`

> 需配置参数 `PostSelfDefineDataType=PostVerifyData`。

---

## 11. 命令回复

设备获取到服务器下发的命令后，需回复执行结果。

```
POST /iclock/devicecmd?SN=${SerialNumber} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
Content-Length: ${XXX}

${CmdRecord}
```

**回复格式：**

```
ID=${XXX}&Return=${XXX}&CMD=${XXX}
```

| 字段 | 说明 |
|---|---|
| `ID` | 服务器下发命令的命令编号 |
| `Return` | 执行结果返回值（见附录1） |
| `CMD` | 服务器下发命令的命令描述 |

> 多条命令回复之间使用 LF 连接。少部分回复会包含其他信息（如 INFO、GetFile 等），具体见各命令说明。

**服务器响应：** `OK`

**示例：**

```
POST /iclock/devicecmd?SN=0316144680030 HTTP/1.1
Host: 58.250.50.81:8011
Content-Length: 143

ID=info8487&Return=0&CMD=DATA
ID=info8488&Return=0&CMD=DATA
ID=info8489&Return=0&CMD=DATA
ID=info7464&Return=0&CMD=DATA
ID=fp7464&Return=0&CMD=DATA
```

---

## 12. 异地考勤

用户出差到异地时，考勤机内无该用户信息，通过异地考勤方式获取用户信息后考勤。

```
GET /iclock/cdata?SN=${SerialNumber}&table=RemoteAtt&PIN=${XXX} HTTP/1.1
Host: ${ServerIP}:${ServerPort}
```

**服务器响应（存在用户信息时）：**

```
HTTP/1.1 200 OK
Content-Length: ${XXX}

DATA UPDATE USERINFO PIN=${XXX}\tName=${XXX}\tPasswd=${XXX}\tCard=${XXX}\tGrp=${XXX}\tTZ=${XXX}\tPri=${XXX}
DATA UPDATE FINGERTMP PIN=${XXX}\tFID=${XXX}\tSize=${XXX}\tValid=${XXX}\tTMP=${XXX}
```

> 响应数据格式同 DATA UPDATE 命令，多条记录之间使用 LF 连接。

---

## 13. 附录

### 附录1：错误码

**通用错误码：**

| 返回值 | 描述 |
|---|---|
| 0 | 成功 |
| -1 | 参数错误 |
| -2 | 传输用户照片数据与给定的 Size 不匹配 |
| -3 | 读写错误 |
| -9 | 传输的模板数据与给定的 Size 不匹配 |
| -10 | 设备中不存在 PIN 所指定的用户 |
| -11 | 非法指纹模板格式 |
| -12 | 非法的指纹模板 |
| -30 | 一体化模板算法版本不一致 |
| -1001 | 容量限制 |
| -1002 | 设备不支持 |
| -1003 | 命令执行超时 |
| -1004 | 数据与设备配置不一致 |
| -1005 | 设备忙 |
| -1006 | 数据太长 |
| -1007 | 内存错误 |
| -1008 | 获取服务器数据失败 |

**Enroll_FP / Enroll_BIO 错误码：**

| 返回值 | 描述 |
|---|---|
| 2 | 对应用户的指纹已经存在 |
| 4 | 登记失败（指纹质量差或三次不一致） |
| 5 | 登记的指纹已在指纹库中存在 |
| 6 | 取消登记 |
| 7 | 设备忙，无法登记 |

**PutFile（Action=SyncData）错误码：**

| 返回值 | 描述 |
|---|---|
| n > 0 | 同步数据，成功处理 n 条指令 |

### 附录2：语言编号

| 编号 | 语言 | 编号 | 语言 | 编号 | 语言 |
|---|---|---|---|---|---|
| 83 | 简体中文 | 84 | 繁体中文 | 69 | 英文 |
| 97 | 西班牙语 | 70 | 法语 | 66 | 阿拉伯语 |
| 80 | 葡萄牙语 | 82 | 俄语 | 71 | 德语 |
| 65 | 波斯语 | 76 | 泰语 | 73 | 印尼语 |
| 74 | 日本语 | 75 | 韩语 | 86 | 越南语 |
| 116 | 土耳其语 | 72 | 希伯来语 | 90 | 捷克语 |
| 68 | 荷兰语 | 105 | 意大利语 | 89 | 斯洛伐克语 |
| 103 | 希腊语 | 112 | 波兰语 | | |

### 附录3：操作代码

| 代码 | 意义 | 代码 | 意义 |
|---|---|---|---|
| 0 | 开机 | 1 | 关机 |
| 2 | 验证失败 | 3 | 报警 |
| 4 | 进入菜单 | 5 | 更改设置 |
| 6 | 登记指纹 | 7 | 登记密码 |
| 8 | 登记HID卡 | 9 | 删除用户 |
| 10 | 删除指纹 | 11 | 删除密码 |
| 12 | 删除射频卡 | 13 | 清除数据 |
| 14 | 创建MF卡 | 15 | 登记MF卡 |
| 16 | 注册MF卡 | 17 | 删除MF卡注册 |
| 18 | 清除MF卡内容 | 19 | 登记数据移到卡中 |
| 20 | 卡中数据复制到机器 | 21 | 设置时间 |
| 22 | 出厂设置 | 23 | 删除进出记录 |
| 24 | 清除管理员权限 | 25 | 修改门禁组设置 |
| 26 | 修改用户门禁设置 | 27 | 修改门禁时间段 |
| 28 | 修改开锁组合设置 | 29 | 开锁 |
| 30 | 登记新用户 | 31 | 更改指纹属性 |
| 32 | 胁迫报警 | 33 | 门铃呼叫 |
| 34 | 反潜 | 35 | 删除考勤照片 |
| 36 | 修改用户其他信息 | 37 | 节假日 |
| 38 | 还原数据 | 39 | 备份数据 |
| 40 | U盘上传 | 41 | U盘下载 |
| 42 | U盘考勤记录加密 | 43 | U盘下载成功后删除记录 |
| 53 | 出门开关 | 54 | 门磁 |
| 55 | 报警 | 56 | 恢复参数 |
| 68 | 注册用户照片 | 69 | 修改用户照片 |
| 70 | 修改用户姓名 | 71 | 修改用户权限 |
| 76 | 修改网络设置IP | 77 | 修改网络设置掩码 |
| 78 | 修改网络设置网关 | 79 | 修改网络设置DNS |
| 80 | 修改连接设置密码 | 81 | 修改连接设置设备ID |
| 82 | 修改云服务器地址 | 83 | 修改云服务器端口 |
| 87 | 修改门禁记录设置 | 88 | 修改人脸参数标志 |
| 89 | 修改指纹参数标志 | 90 | 修改指静脉参数标志 |
| 91 | 修改掌纹参数标志 | 92 | U盘升级标志 |
| 100 | 修改RF卡信息 | 101 | 登记人脸 |
| 102 | 修改人员权限 | 103 | 删除人员权限 |
| 104 | 增加人员权限 | 105 | 删除门禁记录 |
| 106 | 删除人脸 | 107 | 删除人员照片 |
| 108 | 修改参数 | 109 | 选择WIFISSID |
| 110 | proxy使能 | 111 | proxyip修改 |
| 112 | proxy端口修改 | 113 | 修改人员密码 |
| 114 | 修改人脸信息 | 115 | 修改operator的密码 |
| 116 | 恢复门禁设置 | 117 | operator密码输入错误 |
| 118 | operator密码锁定 | 120 | 修改Legic卡数据长度 |
| 121 | 登记指静脉 | 122 | 修改指静脉 |
| 123 | 删除指静脉 | 124 | 登记掌纹 |
| 125 | 修改掌纹 | 126 | 删除掌纹 |

### 附录4：操作记录字段映射

| 操作代码 | 操作对象1 | 操作对象2 | 操作对象3 | 操作对象4 |
|---|---|---|---|---|
| 2 | 若为1:1验证，则为用户工号 | | | |
| 3 | 报警 | 报警原因（见附录5） | | |
| 5 | 被修改的设置项序号 | 新修改后的值 | | |
| 6 | 用户工号 | 指纹序号 | 指纹模板长度 | |
| 9 | 用户工号 | | | |
| 10 | 用户工号 | | | |
| 11 | 用户工号 | | | |
| 12 | 用户工号 | | | |

### 附录5：报警原因

| 代码 | 意义 |
|---|---|
| 50 | Door Close Detected |
| 51 | Door Open Detected |
| 53 | Out Door Button |
| 54 | Door Broken Accidentally |
| 55 | Machine Been Broken |
| 58 | Try Invalid Verification |
| 65535 | Alarm Cancelled |

### 附录6：协议版本规则

**已发布版本：** 2.2.14 / 2.3.0 / 2.4.0 / 2.4.1

**加密协议版本：** 2.4.0 及以上

**版本协商机制：**
1. 设备通过 `pushver` 参数上报当前协议版本
2. 服务器通过 `PushProtVer` 参数返回服务端协议版本
3. 双方比较，**使用较低版本**进行交互
4. 未返回 `PushProtVer` 时，默认为 2.2.14

### 附录7：验证方式

| 值 | 描述 |
|---|---|
| 0 | 指静脉或人脸或指纹或卡或密码（自动识别） |
| 1 | 仅指纹 |
| 2 | 工号验证 |
| 3 | 仅密码 |
| 4 | 仅卡 |
| 5 | 指纹或密码 |
| 6 | 指纹或卡 |
| 7 | 卡或密码 |
| 8 | 工号加指纹 |
| 9 | 指纹加密码 |
| 10 | 卡加指纹 |
| 11 | 卡加密码 |
| 12 | 指纹加密码加卡 |
| 13 | 工号加指纹加密码 |
| 14 | 工号加指纹或卡加指纹 |
| 15 | 人脸 |
| 16 | 人脸加指纹 |
| 17 | 人脸加密码 |
| 18 | 人脸加卡 |
| 19 | 人脸加指纹加卡 |
| 20 | 人脸加指纹加密码 |
| 21 | 指静脉 |
| 22 | 指静脉加密码 |
| 23 | 指静脉加卡 |
| 24 | 指静脉加密码加卡 |
| 25 | 掌纹 |
| 26 | 掌纹加卡 |
| 27 | 掌纹加面部 |
| 28 | 掌纹加指纹 |
| 29 | 掌纹加指纹加面部 |
| 200 | 其他 |

### 附录8：通信加密方案

**算法：** 加密算法库统一封装，设备使用静态库。

**密钥交换流程：**

1. **初始化：** 设备和服务器重连时初始化非对称加密的公私钥
2. **交换公钥：**
   - 设备发送设备公钥 P1 给服务器
   - 服务器返回服务器公钥 P2 给设备
3. **交换因子：**
   - 设备生成因子 R1，用服务器公钥加密发送
   - 服务器用私钥解出 R1，生成因子 R2，用设备公钥加密发送
   - 设备用私钥解出 R2
4. **生成会话密钥：** 双方使用相同的混淆算法，基于 R1 和 R2 生成 `sessionKey`
5. **加密通信：** 后续数据以 `sessionKey` 作为对称加密密钥

**兼容方案：**
- 设备和服务器协议版本不都支持加密 → 明码传输
- 设备和服务器协议版本都支持加密 → 使用数据加密方案
- 对通信数据签名进行 CRC32 校验

### 附录9：异常日志错误码

**错误码格式：** 错误产生端(1位) + 模块(2位) + 类型(1位) + 错误值(4位)

| 错误码 | 描述 |
|---|---|
| 00000000 | 成功 |
| D01E0001 | 探测人脸失败 |
| D01E0002 | 人脸遮挡 |
| D01E0003 | 清晰度不够 |
| D01E0004 | 人脸角度太大 |
| D01E0005 | 活体检测失败 |
| D01E0006 | 提取模板失败 |

**错误产生端（第1位）：**

| 值 | 说明 |
|---|---|
| D | 设备端返回的错误码 |
| S | 软件端返回的错误码 |

**模块（第2-3位）：**

| 值 | 设备端模块 |
|---|---|
| 01 | PUSH通信模块 |
| 02 | 模板处理模块 |
| 03 | 硬件交互模块 |
| 04 | PULL通信模块 |
| 05 | 脱机通信模块 |
| 06 | 数据中转模块 |
| 07 | 许可服务模块 |

**类型（第4位）：** E = ERROR

### 附录10：生物识别类型索引

| 索引 | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 类型 | 通用 | 指纹 | 近红外人脸 | 声纹 | 虹膜 | 视网膜 | 掌纹 | 指静脉 | 掌静脉 | 可见光人脸 | 可见光手掌 |

**归属说明：** 索引 1-8 归属近红外，索引 9-10 归属可见光，索引 0 为通用。

**多模态参数格式（以冒号隔开的按位定义）：**

| 参数名 | 说明 | 示例 |
|---|---|---|
| `MultiBioDataSupport` | 支持模板的生物识别类型 | `0:1:1:0:0:0:0:0:0:0:0` = 支持指纹+近红外人脸 |
| `MultiBioPhotoSupport` | 支持图像的生物识别类型 | 同上格式 |
| `MultiBioVersion` | 各类型算法版本 | `0:10.0:7.0:0:0:0:0:0:0:0:0` = 指纹10.0+人脸7.0 |
| `MaxMultiBioDataCount` | 模板最大容量 | `0:10000:3000:0:0:0:0:0:0:0:0` |
| `MaxMultiBioPhotoCount` | 照片最大容量 | 同上格式 |
| `MultiBioDataCount` | 当前模板数量 | 同上格式 |
| `MultiBioPhotoCount` | 当前照片数量 | 同上格式 |

---

## 14. 混合识别协议规范说明

支持多模态生物识别的设备遵循以下规范：

### 14.1 统一接口

| 操作 | 统一接口 |
|---|---|
| 服务器下发模板 | `DATA UPDATE BIODATA`（一体化模板） |
| 服务器下发照片 | `DATA UPDATE BIOPHOTO`（比对照片） |
| 服务器查询模板 | `DATA QUERY BIODATA` |
| 服务器查询模板数量 | `DATA QUERY BIODATA`（返回数量） |
| 设备上传模板 | `table=BIODATA`（上传一体化模板） |
| 设备上传照片 | `table=OPERLOG`（上传比对照片） |

### 14.2 容量上报

设备在注册时推送支持的最大数量（`MaxMultiBioDataCount`、`MaxMultiBioPhotoCount`），通过推送配置信息实时上传当前数量。

### 14.3 实时上传

设备登记的生物识别模板/比对照片会实时上传给服务器。

### 14.4 优化策略

服务器可根据 `MultiBioVersion` 判断设备模板版本号，优先下发模板（而非比对照片），效率更高。

> **注意：** 针对相同人员的同一生物识别类型，如已存在算法版本一致的模板，不要同时下发模板和照片，只会增加设备负担。

---

## 15. 与安防PUSH协议的主要差异

> 以下对比仅供参考，帮助已有安防PUSH对接经验的开发者快速理解差异。

| 对比项 | 考勤PUSH V5.8 | 安防PUSH V7.3 |
|---|---|---|
| Push协议版本 | V2.4.2 | V3.1.2 |
| 设备注册 | 无独立注册步骤 | 有 `/iclock/registry` 注册流程 |
| 命令获取 | `GET /iclock/getrequest?SN=xxx` | `POST /iclock/push?SN=xxx` |
| 配置下发 | 初始化时直接返回 | 有独立 `/iclock/push` 配置下载 |
| 实时事件 | 无 rtlog/rtstate | 有 rtlog（实时事件）/ rtstate（实时状态） |
| 核心数据 | 考勤记录（ATTLOG）、考勤照片（ATTPHOTO） | 门禁事件（rtlog）、门禁状态（rtstate） |
| 上传数据类型 | ATTLOG/ATTPHOTO/OPERLOG/IDCARD/BIODATA/ERRORLOG 等 16 种 | rtlog/rtstate/user 等 |
| 身份证功能 | 支持（人证协议） | 不支持 |
| 门禁功能 | 支持（AccGroup/AccTimeZone/AccHoliday 等） | 支持（更完整） |
| Token 机制 | 仅 ping 使用 Cookie:token | push 请求均使用 Cookie:token |

---

## 16. 对接注意事项

### 16.1 编码问题

- 用户姓名在中文设备上使用 **GB2312** 编码，其他语言使用 UTF-8
- 短消息内容同样区分中文（GB2312）和其他（UTF-8）
- 身份证相关字段统一使用 UTF-8

### 16.2 数据量限制

- 单次下发数据量不得超过 **900KB**
- 指纹模版 `Size` 为 Base64 编码后的长度
- 短消息内容最大 **320 字节**

### 16.3 协议版本兼容

- 新开发客户端必须支持 `pushver ≥ 2.2.14`
- 加密通信需要 `pushver ≥ 2.4.0`
- 异常日志需要 `pushver ≥ 2.4.1`
- 身份证相关功能需要 `pushver ≥ 2.3.0`（上传身份证信息）或 `≥ 2.4.0`（身份证考勤记录/照片）

### 16.4 时间戳机制

- 时间戳存在缺陷：修改时间会导致断点续传失败
- 新架构固件已废弃时间戳，仅为兼容老服务器保留
- 服务器将时间戳置 0 时，设备重新上传对应数据

### 16.5 卡号格式

支持两种格式：
- **十六进制：** `[%02x%02x%02x%02x]`，如卡号 123456789 → `Card=[15CD5B07]`
- **字符串：** 如卡号 123456789 → `Card=123456789`

### 16.6 多模态生物识别

- 一体化模板统一使用 `BIODATA` 表名，通过 `Type` 字段区分类型
- 比对照片统一使用 `BIOPHOTO` 表名
- 不要对同一人员的同一生物识别类型同时下发模板和照片

---

