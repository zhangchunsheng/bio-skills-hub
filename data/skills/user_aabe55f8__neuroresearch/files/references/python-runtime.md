# Python 运行前依赖自检约定（内置标准流程）

任何需要运行 Python 的分析 / 出图脚本，在正式计算前**必须先做依赖自检**：

> **检测本任务需要哪些包 → 检查是否已安装 → 缺失则自动安装**

这样技能在任意干净环境都能「开箱即跑」，不会因 `ImportError` / `ModuleNotFoundError` 卡住。本约定是强制流程，不是可选项。

## 一、标准自检前导（每个 Python 脚本开头都放这段）

```python
import importlib.util, subprocess, sys   # 必须 importlib.util（import importlib 不保证加载 util 子模块）

# 1) 本任务需要的包（按实际任务增删，列全再跑）
REQUIRED = ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "seaborn"]

# 2) 检测缺失
missing = [p for p in REQUIRED if importlib.util.find_spec(p) is None]

# 3) 缺失则安装（用当前解释器对应的 pip，避免污染全局）
if missing:
    print(f"[setup] 安装缺失依赖: {missing}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])

# 4) 正式 import（安装后必能成功）；无显示环境（服务器/CI）必须先设 Agg 后端
import matplotlib
matplotlib.use('Agg')                    # 无显示环境必须（所有脚本统一）
import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import matplotlib.pyplot as plt
import seaborn as sns

# 5) 打印版本，随脚本交付（可复现）
print("numpy", np.__version__, "| pandas", pd.__version__,
      "| scipy", scipy.__version__, "| statsmodels", statsmodels.__version__)
```

> 若安装或 import 失败（如网络受限），**明确报告错误并停止**，绝不能在产出里写「结果已出」而实际没跑。

## 二、任务 → 所需包 速查

| 任务 | 在 REQUIRED 中列出 |
|------|-------------------|
| 基础统计（t / ANOVA / 相关） | numpy, pandas, scipy, statsmodels |
| 投稿级统计图 | matplotlib, seaborn（+ 上者） |
| 生存分析（KM / log-rank） | lifelines（+ 上者） |
| 单细胞 scRNA-seq | scanpy, anndata, leidenalg |
| 富集分析 | gseapy |
| 读写 .xlsx | openpyxl（写入）；pandas 读 .xlsx 依赖 openpyxl |
| 生成 .docx（无 tencent-docx 时兜底） | python-docx（见 academic-word-template.md §一） |
| 文献管理表格 | pandas, openpyxl |

> 跨任务脚本把上表涉及的包合并进同一个 REQUIRED 即可。

## 三、环境引导与 venv（统一入口 ensure_env.py）

本技能绘图依赖装在受管理 venv 里，**不要用裸 `python` 直接 import 判定装没装**（会误判为缺失）。统一走 `scripts/ensure_env.py`：

```bash
# 返回一个「能 import 全部绘图依赖」的解释器路径（跨平台、幂等、秒退）
PY=$(python scripts/ensure_env.py)
$PY your_plot.py          # 之后一律用 $PY 跑绘图脚本
```

- **原理**：从 `sys.executable` 推导受管理 venv `<root>/binaries/python/envs/default`；已就绪则秒退返回路径，缺包才补装。
- **幂等**：重复跑不会重装；换机器/换用户名不硬编码路径。
- **兜底**：不在受管理结构内时，落到用户级 `~/.workbuddy/python_envs/prism_plot`。
- **R 流程不在此列**：DESeq2/edgeR 等走本地 R / RStudio（`scripts/bioinfo_rna_seq.R`），不强行 pip。

## 四、常见报错排查

| 现象 | 原因 | 处理 |
|------|------|------|
| `EBADENGINE` / `requires python >= 3.x` | 包版本与本机 Python 不兼容 | 用 `install_binary` 装匹配版本，或指定兼容版本 `pip install pkg==x.y.z` |
| `ModuleNotFoundError` 但明明装过 | 用错解释器（基础 python vs venv） | 统一用 `ensure_env.py` 返回的 `$PY` |
| `pip` 权限拒绝（Permission denied） | 尝试写系统目录 | 加 `--user` 或改用 venv；**绝不 sudo/管理员硬装** |
| 网络超时 / 下载慢 | 默认 PyPI 源受限 | 换国内镜像（见第五节） |
| `UnicodeEncodeError`（中文报错） | Windows 控制台默认 GBK | 脚本顶部 `sys.stdout.reconfigure(encoding="utf-8")` |
| 图上中文显示为方块 | 字体缺中文字形 | `apply_prism_theme(font_family=...)` 指定中文字体，或负号处理 |
| `python -m venv` 报「复制启动器失败 / 文件锁定」（Windows） | 默认 venv 在 Windows 上复制基础解释器 launcher 被文件锁阻断（受管理 Python 3.13 隔离目录常见，导致整个 venv 创建回滚） | 建 venv 时加 `--copies` 强制完整文件拷贝：`python -m venv --copies <path>`；或优先走 `scripts/ensure_env.py`，若它也卡 launcher 则改用 `--copies` 重建 |

## 五、pip 镜像源（国内加速，可选）

```bash
pip install pkg -i https://pypi.tuna.tsinghua.edu.cn/simple
# 或阿里云 https://mirrors.aliyun.com/pypi/simple/
```

> 仅当默认源超时/限速时用；交付脚本里**不要写死镜像源**，保持可移植。

## 六、版本锁定与可复现

- **打印版本**：脚本结尾打印关键包版本，与结果一并交付（见第一节第 5 步）。
- **锁定**：正式交付可附 `requirements.txt`（`pip freeze` 生成），但**不强制**——本技能强调"开箱即跑"，优先让自检自动补齐，而非要求用户先装环境。
- **随机种子**：一切含随机性的分析设 `np.random.default_rng(seed)` 或 `random_state`，参数、参考基因组版本同样记录。

## 七、改动后自检（强制）

每次修改 `scripts/prism_theme.py` 或增删 reference 后，跑一遍自检脚本抓「版本号漂移」「文档与磁盘不同步」并做引擎回归：

```bash
PY=$(python scripts/ensure_env.py) && $PY scripts/selfcheck.py
# 期望：PASS 全绿、FAIL 0；引擎缺依赖时 B 部分 SKIP 不判失败。
```

- 退出码 0 = 全绿；非 0 = 有 FAIL（版本/文档漂移），**先修再提交**。
- 自检脚本本身零第三方依赖、秒退、只读，不装任何包。

## 八、与本技能其它模块的配合

- 统计分析与出图见 `statistical-analysis.md`（Python 优先）。
- 生信（富集 / 单细胞）见 `bioinformatics.md`。
- 表格维护（纳入文献清单等）见 `literature-review.md`（pandas / openpyxl 为 fallback）。
