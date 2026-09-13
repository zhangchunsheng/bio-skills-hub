# edsdk.py 工具使用详解

## 基础路径

```
C:\Users\Administrator\.workbuddy\plugins\cache\workbuddy-builtin\skill-tencent-local-office-edit\0.0.1
```

## 三条核心命令

| 命令 | 作用 |
|------|------|
| `python3 edsdk.py list [sheet]` | 列出工具清单 |
| `python3 edsdk.py schema <工具名>` | 查询单个工具参数 |
| `python3 edsdk.py call <工具名> [k=v ...] [--json '{...}']` | 调用工具 |

## 常用工具

### 文件管理
- `get_pool_status`：查看已打开文档池，获取 file_id
- `open_file`：打开本地文件（返回 file_id）
- `save_file`：保存（file_path 省略则覆盖原文件）
- `close_file`：关闭（实时编辑时不要主动调）

### 排班表操作
- `sheet_get_sheet_info`：获取子表列表（sheet_id, 名称, 行列数）
- `sheet_get_cell_data`：读取区域数据（start_row, start_col, end_row, end_col, return_csv=true）
- `sheet_insert_dimension`：插入行/列（dimension_type=row, index, count, direction=after）
- `sheet_set_range_value_by_csv`：批量写入CSV数据（start_row, start_col, csv_data）
- `sheet_merge_cell`：合并单元格（start_row, start_col, end_row, end_col, merge_type=all）
- `sheet_set_border`：设置边框（border_positions=[0,1,2,3,4,5], border_style=1）
- `sheet_set_cell_style`：设置样式（format={bold, horizontal_alignment, vertical_alignment, font_size}）

## 获取 file_id 的标准流程

```bash
# 1. 用 present_files 工具打开文件给用户预览
# 2. 等待2秒后查询文档池
sleep 2
python3 edsdk.py call get_pool_status
# 3. 从返回结果中取 file_id（不要用文件路径当 file_id）
```

## 批量写入 CSV 数据的正确方式

### 问题
- 直接在 shell 中传 csv_data 参数，中文和特殊字符易被 shell 转义破坏
- CSV 每行列数必须完全一致，否则报错
- 文件有 BOM 会导致首行解析异常

### 正确方法：Python subprocess + --json

```python
import subprocess, json, csv

# 1. 用 csv.writer 生成规整 CSV（自动处理引号转义）
rows = [
    ['标题行', '', '', '', '', '', '', '', '', '', ''],
    ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日', '积扣假', '总积假', '备注'],
    # ... 16人排班数据 ...
]
# 每行必须11列，用空字符串补齐

# 2. 写入临时文件（无 BOM）
csv_path = 'temp_schedule.csv'
with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

# 3. 读取并通过 --json 传参
with open(csv_path, 'r', encoding='utf-8') as f:
    csv_content = f.read()

payload = {
    'file_id': '<file_id>',
    'sheet_id': '000001',
    'start_row': 693,
    'start_col': 0,
    'csv_data': csv_content
}

result = subprocess.run(
    ['python3', 'edsdk.py', 'call', 'sheet_set_range_value_by_csv',
     '--json', json.dumps(payload)],
    capture_output=True, text=True, encoding='utf-8',
    cwd='<edsdk目录>'
)
```

### 行数不足时的处理

```bash
# 先插入足够行数
python3 edsdk.py call sheet_insert_dimension \
  file_id=<id> sheet_id=000001 \
  dimension_type=row index=693 count=21 direction=after
# 再写入数据
```

## 格式化排班表区块

```bash
# 1. 合并标题行（A:K）
python3 edsdk.py call sheet_merge_cell \
  file_id=<id> sheet_id=000001 \
  start_row=693 start_col=0 end_row=693 end_col=10 merge_type=all

# 2. 添加边框（表头到最后一行，A-H列）
python3 edsdk.py call sheet_set_border \
  file_id=<id> sheet_id=000001 \
  start_row=694 start_col=0 end_row=711 end_col=7 \
  border_positions='[0,1,2,3,4,5]' border_style=1 border_color=000000

# 3. 设置样式（通过 Python --json 传 format 对象）
# 标题：bold + center + font_size=14
# 表头：bold + center
# 数据：center
```

## 排班表区块行结构（21行/周）

| 行偏移 | 内容 |
|--------|------|
| +0 | 标题："2026年南医三院中心药房X月份排班表" |
| +1 | 表头：,周一,周二,...,周日,积扣假（天）,总积假（天）,备注 |
| +2 | 日期：,31日,1日,... |
| +3 ~ +18 | 16人排班（姓名+7天班次+3空列） |
| +19 | 说明：班次时间说明 |
| +20 | 备注：规则说明或特殊标注 |

## 坐标规则
- 所有行列索引均为 0-based
- sheet_id 通常为 "000001"（单 Sheet 文件）
- file_id 通过 get_pool_status 获取，不要用文件路径代替
