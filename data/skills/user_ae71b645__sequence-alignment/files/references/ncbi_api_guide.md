# NCBI BLAST API 指南

## API 端点

基础 URL：`https://blast.ncbi.nlm.nih.gov/Blast.cgi`

## 请求命令

### Put 命令（提交搜索）
提交一个新的 BLAST 搜索请求。

**参数：**
- `CMD=Put` - 必填
- `PROGRAM` - BLAST 程序（blastn、blastp、blastx、tblastn、tblastx）
- `DATABASE` - 目标数据库名称
- `QUERY` - 查询序列
- `EXPECT` - E-value 阈值（默认：10）
- `HITLIST_SIZE` - 返回的最大命中数（默认：50）
- `FORMAT_TYPE` - 响应格式（HTML、Text、XML、JSON2）

**示例：**
```
CMD=Put&PROGRAM=blastn&DATABASE=nt&QUERY=ATGCGTACG
```

### Get 命令（获取结果）
使用请求 ID（RID）获取结果。

**参数：**
- `CMD=Get` - 必填
- `RID` - Put 命令返回的请求 ID
- `FORMAT_TYPE` - 输出格式

**示例：**
```
CMD=Get&RID=ABCDEF123&FORMAT_TYPE=XML
```

### Delete 命令（取消搜索）
取消正在运行的搜索。

**参数：**
- `CMD=Delete` - 必填
- `RID` - 待取消的请求 ID

## 响应状态

检查搜索状态时，注意响应中的以下标识：

- `Status=WAITING` - 搜索正在进行中
- `Status=READY` - 搜索已成功完成
- `Status=FAILED` - 搜索失败
- `Status=UNKNOWN` - RID 无效

## 速率限制

NCBI 建议：
- 每 3 秒最多发起 1 次请求
- 轮询间隔不要短于 10 秒
- 根据 RTOE（Request Time of Execution，预计执行时间）设置合理的等待时间

## 错误处理

常见的 HTTP 错误：
- `429 Too Many Requests` - 超出速率限制，需等待后重试
- `500 Internal Server Error` - 服务器错误，采用退避策略重试
- `502 Bad Gateway` - 临时性问题，延迟后重试

## 输出格式

### XML（推荐）
- 完整的比对数据
- 可进行结构化解析
- 支持所有 BLAST 特性

### JSON2
- 现代 JSON 格式
- 比 XML 更易解析
- 大多数程序均支持

### Text
- 人类可读的格式
- 程序化处理能力有限
- 适合快速查看

## Python 示例

```python
import urllib.request
import urllib.parse
import time

# 提交搜索
params = {
    'CMD': 'Put',
    'PROGRAM': 'blastn',
    'DATABASE': 'nt',
    'QUERY': 'ATGCGTACGTAGCTAGCTAG',
    'FORMAT_TYPE': 'XML'
}
data = urllib.parse.urlencode(params).encode('utf-8')
req = urllib.request.Request('https://blast.ncbi.nlm.nih.gov/Blast.cgi', 
                              data=data, method='POST')
response = urllib.request.urlopen(req)
result = response.read().decode('utf-8')

# 提取 RID
rid = result[result.find('RID = ') + 6:].split('\n')[0].strip()

# 轮询结果
while True:
    time.sleep(10)
    check_params = {'CMD': 'Get', 'RID': rid}
    check_data = urllib.parse.urlencode(check_params).encode('utf-8')
    check_req = urllib.request.Request(url, data=check_data, method='POST')
    check_resp = urllib.request.urlopen(check_req)
    check_result = check_resp.read().decode('utf-8')
    if 'Status=READY' in check_result:
        break

# 获取结果
get_params = {'CMD': 'Get', 'RID': rid, 'FORMAT_TYPE': 'XML'}
```

## NCBI 使用政策

- 请求中尽可能包含工具名称和邮箱信息
- 不要向服务器发起超负荷请求
- 适当情况下缓存结果
- 遵守 Entrez 使用指南：https://www.ncbi.nlm.nih.gov/home/about/policies/
