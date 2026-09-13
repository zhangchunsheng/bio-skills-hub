# 缓存清理指南

> 本指南说明如何清理项目中的缓存文件，保持目录干净。

---

## 🧹 为什么需要清理缓存？

Python 运行时会自动生成以下缓存文件：

| 文件类型 | 说明 | 是否必需 |
|---------|------|---------|
| `__pycache__/` | Python字节码缓存 | 否（可自动生成） |
| `*.pyc` | 编译后的字节码 | 否（可自动生成） |
| `.pytest_cache/` | pytest测试缓存 | 否（可自动生成） |
| `*.zip` | 备份文件 | 否（二进制文件） |
| `*.xlsx` | Excel导出 | 否（二进制文件） |

这些文件：
- ❌ 不应提交到版本控制
- ❌ 占用额外空间
- ❌ 可能导致上传失败
- ✅ 可以安全删除（运行时自动重建）

---

## 🚀 快速清理

### 方法1：使用清理脚本（推荐）

```bash
# 预览清理内容
python scripts/cleanup_cache.py

# 实际执行清理
python scripts/cleanup_cache.py --execute
```

### 方法2：手动清理

```bash
# Windows
rm -rf scripts/__pycache__ tests/__pycache__ .pytest_cache
rm -f scripts/*.pyc tests/*.pyc

# Linux/Mac
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
rm -rf .pytest_cache
```

### 方法3：使用 git 清理

```bash
# 清理未跟踪的文件（谨慎使用）
git clean -fd

# 只清理忽略的文件
git clean -fdX
```

---

## 🛡️ 防止缓存文件出现

### 1. .gitignore 配置

项目已配置 `.gitignore`，自动忽略以下文件：

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so

# 测试/构建产物
.pytest_cache/
.cache/
.coverage
htmlcov/

# 二进制文件
*.zip
*.xlsx
*.xls
*.docx
*.doc
*.pdf
*.png
*.jpg
```

### 2. 环境变量（可选）

设置环境变量禁止生成 `.pyc` 文件：

```bash
# Windows
set PYTHONDONTWRITEBYTECODE=1

# Linux/Mac
export PYTHONDONTWRITEBYTECODE=1

# 或在代码中
import sys
sys.dont_write_bytecode = True
```

### 3. pytest 配置

在 `pytest.ini` 或 `pyproject.toml` 中禁用缓存：

```ini
[pytest]
addopts = -p no:cacheprovider
```

---

## 📋 定期维护

### 建议的清理频率

| 场景 | 建议 |
|------|------|
| 日常开发 | 每周清理一次 |
| 提交代码前 | 必须清理 |
| 导出表格后 | 清理二进制文件 |
| 运行测试后 | 可选清理 |

### 自动化清理（可选）

#### Windows 任务计划

```batch
@echo off
cd /d "D:\claude 开发\skill of me\skill-my-fund-manager"
python scripts/cleanup_cache.py --execute
```

#### Linux/Mac crontab

```bash
# 每周日清理
0 0 * * 0 cd /path/to/skill-my-fund-manager && python scripts/cleanup_cache.py --execute
```

---

## 🔍 检查缓存状态

### 查看缓存文件

```bash
# 查找所有缓存目录
find . -type d -name "__pycache__"

# 查找所有 .pyc 文件
find . -type f -name "*.pyc"

# 查找所有二进制文件
find . -type f \( -name "*.zip" -o -name "*.xlsx" -o -name "*.pyc" \)
```

### 统计缓存大小

```bash
# 统计缓存目录大小
du -sh __pycache__ .pytest_cache

# 统计所有缓存文件大小
find . -type f \( -name "*.pyc" -o -name "*.zip" -o -name "*.xlsx" \) -exec du -sh {} +
```

---

## ⚠️ 注意事项

### 可以安全删除的文件

- ✅ `__pycache__/` - Python会自动重建
- ✅ `*.pyc` - Python会自动重建
- ✅ `.pytest_cache/` - pytest会自动重建
- ✅ `*.zip` - 备份文件，可重新创建
- ✅ `*.xlsx` - 导出文件，可重新生成

### 不要删除的文件

- ❌ `*.py` - 源代码文件
- ❌ `*.json` - 数据文件（roster.json等）
- ❌ `*.csv` - 导出的数据文件
- ❌ `*.md` - 文档文件

### 删除后的影响

| 文件类型 | 删除后影响 | 恢复方式 |
|---------|-----------|---------|
| `__pycache__/` | 首次运行稍慢 | 运行Python自动重建 |
| `*.pyc` | 首次运行稍慢 | 运行Python自动重建 |
| `.pytest_cache/` | 首次测试稍慢 | 运行pytest自动重建 |
| `*.zip` | 备份丢失 | 重新运行备份脚本 |
| `*.xlsx` | 导出文件丢失 | 重新运行导出脚本 |

---

## 🎯 最佳实践

1. **提交前清理**：每次提交代码前运行清理脚本
2. **定期维护**：每周清理一次缓存文件
3. **使用 .gitignore**：确保配置正确，防止意外提交
4. **备份重要文件**：将备份文件保存到项目外的目录
5. **文档记录**：记录清理操作，便于团队协作

---

## 📚 相关文档

- [.gitignore 配置](.gitignore) - 忽略规则
- [清理脚本](scripts/cleanup_cache.py) - 自动化清理
- [数据备份](scripts/data_backup.py) - 备份工具
- [表格导出](scripts/export_table.py) - 导出工具

---

*最后更新：2026-07-29*
