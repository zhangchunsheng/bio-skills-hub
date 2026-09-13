# tests/

本目录包含 novel-assistant-pro v2.0.0 的单元测试与 smoke test。

## 文件清单

| 文件 | 用途 | 运行命令 |
|---|---|---|
| `test_compress_memory.py` | compress_novel_memory.py 的单元测试 | `python3 -m unittest tests.test_compress_memory` |
| `test_validate_memory.py` | validate_novel_memory.py 的单元测试 | `python3 -m unittest tests.test_validate_memory` |
| `test_smoke.py` | 包完整性 smoke test | `python3 -m unittest tests.test_smoke` |
| `test_skill_static.py` | 静态校验测试 | `python3 -m unittest tests.test_skill_static` |

## 运行所有测试

```bash
python3 -m unittest discover tests/ -v

# 或使用 pytest
python3 -m pytest tests/ -v
```

## CI 集成建议

```yaml
# .github/workflows/test.yml
name: tests
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install python-docx pytest
      - run: python3 -m pytest tests/ -v
```

## 验收门禁

所有测试必须通过（`OK`）才能合并 PR 或升级版本。

| 测试类型 | 当前通过率 |
|---|---|
| 单元测试 | 待运行 |
| 静态校验 | 0 错误 0 警告 |
| Smoke test | 待运行 |
