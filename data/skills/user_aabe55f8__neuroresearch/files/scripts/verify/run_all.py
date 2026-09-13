#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_all.py — prism-style-plot 一键回归入口

用法(遵循技能环境约定,先用 ensure_env.py 拿到 venv 解释器,再运行本脚本):
    PY=$(python ../../scripts/ensure_env.py 2>/dev/null || python scripts/ensure_env.py)
    $PY scripts/verify/run_all.py

    性能优化(v2.5.7):13 个验证脚本彼此独立、产物前缀互不冲突,默认**并行**执行
    (进程池,worker 数 = min(CPU 核心数, 脚本数)),墙钟时间约为串行 1/N。
    串行耗时主要来自每个子进程都重头 import matplotlib+scipy(~1-2s)×13;
    并行后这部分被压到单进程 import 时间量级。
    两类脚本例外,强制**串行**执行(见 SERIAL_SCRIPTS):
      - verify11_deep_edge.py 含**墙钟耗时断言**(3×1000 点 < 5s),
        并行抢 CPU 时可能超时误报 → 放在并行池之后独占运行,断言才有效。
    - 用 --workers N 显式指定并发数(N=1 即退回纯串行,便于调试);
    - 用 --keep-output 在全部通过后保留 output/ 产物供人工复查;
    - 用 --quick 或 --only <档位|脚本> 只跑必要子集,不必次次全套(见 PRESETS);
    - 退出码:0 = 全部通过;1 = 存在失败。

    分档原则(v2.5.7,用户约定"按改动类型选档,不必次次全套"):
      --quick   快速档:跳过 3 个深度脚本(verify9/10/11),浅层 10 个并行 ~30s
                ——只改文案/参数默认值/注释时用
      --only stats  统计档:verify1/2/4/9/10/11——改了统计逻辑(ttest/ANOVA/twoway/
                深度矩阵/边界)时用,~80s
      --only plot   绘图档:verify3a/3b/3c/5/6/7/8——改了绘图封装/布局/点径/ylim 时用
      --only edge   边界档:verify11 单独跑深度边界/性能
      默认(无参数)= 全套 13 个(改动公共 API/大重构时用)

新增验证用例:把脚本放进本目录,命名 verifyN_*.py,并在 VERIFY_SCRIPTS 注册。
"""

# 含墙钟耗时断言等"必须独占 CPU"的脚本:并行池跑完后逐个串行执行。
# 放进来前先确认:该脚本是否真对运行时刻敏感(耗时断言/性能回归)。
SERIAL_SCRIPTS = [
    "verify11_deep_edge.py",  # [8] 3×1000 点绘图 < 5s 的墙钟断言,并行下会误报
]
import argparse
import concurrent.futures as cf
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")

# 按依赖顺序注册:verify_common 无独立入口,其余依次执行
VERIFY_SCRIPTS = [
    "verify1_column.py",
    "verify2_others.py",
    "verify3a_dot_size.py",       # v2.3.0 拆分自 verify3_edge.py（点径+配色+非参数）
    "verify3b_zorder_layout.py",  # v2.3.0 拆分自 verify3_edge.py（抖动+zorder+标签）
    "verify3c_edge_cases.py",     # v2.3.0 拆分自 verify3_edge.py（统计边界+3 表型+报告补强）
    "verify4_twoway_posthoc.py",
    "verify5_grouped_annotated.py",
    "verify6_figsize_recommend.py",
    "verify7_ylim_small.py",      # v2.5.1 新增：ylim<1 值域回归（细粒度步长 + data_max 收集）
    "verify8_ylim_small_allsigns.py",  # v2.5.2 新增：<1 修复全图型推广（下限分级 + boxplot 边框 + violin/grouped/负值）
    "verify9_deep_matrix.py",     # v2.3.4~v2.3.8 深度回归：18 种析因设计矩阵（组数×样本量×交互形态）
    "verify10_deep_others.py",    # 深度回归：其他表型（含 figsize 关键词覆盖）
    "verify11_deep_edge.py",      # v2.5.5 新增：深度边界/性能回归（NaN/inf 过滤、空组、n=1、pie/xy_fit 预检、palette 空列表、_conflict/overlap 向量化）
]

# ---- 按"改动类型"分档的预设别名(v2.5.7)----
# 选择原则:统计逻辑改动 → stats;绘图封装/布局/点径/ylim 改动 → plot;
# 只改文案/参数默认值/注释 → quick(跳过深度回归);深度边界/性能 → edge。
PRESETS = {
    "stats": [
        "verify1_column.py",          # 分组比较 ttest/ANOVA/箱线/小提琴
        "verify2_others.py",          # 其他表型统计(列联/生存/XY)
        "verify4_twoway_posthoc.py",  # Two-way 事后比较
        "verify9_deep_matrix.py",     # 析因矩阵 18 设计(最重)
        "verify10_deep_others.py",    # 其他表型深度回归
        "verify11_deep_edge.py",      # 深度边界/性能
    ],
    "plot": [
        "verify3a_dot_size.py",           # 点径/配色/非参数
        "verify3b_zorder_layout.py",      # 抖动/zorder/标签
        "verify3c_edge_cases.py",         # 统计边界+3 表型+报告
        "verify5_grouped_annotated.py",   # 分组简单效应标注
        "verify6_figsize_recommend.py",   # 画布推荐层
        "verify7_ylim_small.py",          # ylim<1 值域
        "verify8_ylim_small_allsigns.py", # ylim<1 全图型推广
    ],
    "quick": [   # 跳过 3 个深度脚本,浅层并行 ~30s
        "verify1_column.py",
        "verify2_others.py",
        "verify3a_dot_size.py",
        "verify3b_zorder_layout.py",
        "verify3c_edge_cases.py",
        "verify4_twoway_posthoc.py",
        "verify5_grouped_annotated.py",
        "verify6_figsize_recommend.py",
        "verify7_ylim_small.py",
        "verify8_ylim_small_allsigns.py",
    ],
    "edge": ["verify11_deep_edge.py"],
}


def _run_one(script_name, python_exe):
    """在独立子进程中跑单个验证脚本,返回 (name, rc, stdout, stderr)。"""
    path = os.path.join(HERE, script_name)
    try:
        r = subprocess.run(
            [python_exe, path],
            cwd=HERE,
            capture_output=True,
            text=True,
        )
        return script_name, r.returncode, r.stdout, r.stderr
    except Exception as e:  # noqa: BLE001
        return script_name, -1, "", f"无法启动子进程: {e}"


def _emit(name, rc, stdout, stderr):
    """打印单个脚本的结果与输出,保持可读。"""
    status = "PASS" if rc == 0 else "FAIL"
    print(f"\n=== {name}  ->  [{status}] (rc={rc}) ===")
    if stdout:
        # 末尾去多余空行
        print(stdout.rstrip("\n"))
    if rc != 0 and stderr:
        print(f"--- {name} stderr ---")
        print(stderr.rstrip("\n"))


def main():
    ap = argparse.ArgumentParser(description="prism-style-plot 一键回归")
    ap.add_argument("--keep-output", action="store_true",
                    help="回归通过后保留 output/ 产物(默认清理)")
    ap.add_argument("--workers", type=int, default=0,
                    help="并发子进程数(默认 0 = 自动=min(CPU核心,脚本数);1 = 纯串行)")
    ap.add_argument("--quick", action="store_true",
                    help="快速档:跳过 3 个深度脚本(verify9/10/11),浅层 10 个并行 ~30s")
    ap.add_argument("--only", default="",
                    help="只跑指定脚本/档位(逗号分隔;档位: quick/stats/plot/edge;"
                         "也可脚本名或数字如 9,11;空=全部)")
    args = ap.parse_args()

    python_exe = sys.executable
    selected = []
    # 合并 --quick 与 --only:--quick 等价于 --only quick
    keys = ["quick"] if args.quick else []
    if args.only.strip():
        keys += [k.strip() for k in args.only.replace(" ", "").split(",")
                 if k.strip()]
    for k in keys:
        if k in PRESETS:
            selected.extend(PRESETS[k])
            continue
        matched = [s for s in VERIFY_SCRIPTS
                   if s == k or s.startswith(f"verify{k}")
                   or s.split(".")[0] == k]
        if not matched:
            print(f"[run_all] 警告: --only 无法匹配 {k!r}(忽略)")
        selected.extend(matched)
    # 去重保序
    selected = list(dict.fromkeys(selected))
    if not selected:
        print("[run_all] 没有可运行的脚本,退出")
        return 0

    pool_scripts = [s for s in selected if s not in SERIAL_SCRIPTS]
    serial_scripts = [s for s in selected if s in SERIAL_SCRIPTS]
    n = len(selected)
    workers = args.workers if args.workers and args.workers > 0 \
        else min(os.cpu_count() or 1, len(pool_scripts))

    os.makedirs(OUT_DIR, exist_ok=True)
    print(f"[run_all] 解释器: {python_exe}")
    print(f"[run_all] 输出目录: {OUT_DIR}")
    print(f"[run_all] 并行 worker 数: {workers} (池内 {len(pool_scripts)} 个脚本, "
          f"串行 {len(serial_scripts)} 个: {', '.join(serial_scripts) or '无'})\n")

    t0 = time.time()
    results = {}
    # 并行池:完成顺序打印,避免输出交错
    if pool_scripts:
        with cf.ProcessPoolExecutor(max_workers=workers) as ex:
            futures = {ex.submit(_run_one, name, python_exe): name
                       for name in pool_scripts}
            for fut in cf.as_completed(futures):
                name, rc, out, err = fut.result()
                results[name] = (rc == 0)
                _emit(name, rc, out, err)
    # 串行段:独占 CPU 的脚本(耗时断言)逐个跑,保证计时准确
    for name in serial_scripts:
        _, rc, out, err = _run_one(name, python_exe)
        results[name] = (rc == 0)
        _emit(name, rc, out, err)

    elapsed = time.time() - t0
    n_pass = sum(1 for v in results.values() if v)
    n_total = len(results)
    print("\n" + "=" * 56)
    for name, ok in results.items():
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print("=" * 56)
    print(f"回归结果: {n_pass}/{n_total} 通过  |  墙钟耗时 {elapsed:.1f}s")

    if n_pass == n_total and not args.keep_output:
        # 清理产物但保留目录(输出是验证副产物,不随技能包累积)
        # v2.5.3:由逐文件 os.remove(Windows 回收站/占用不可用时 94 个文件逐个
        # 失败,只留数字提示)改为 shutil.rmtree 整目录删除 + 重建——单次操作,
        # 要么干净删除要么一次报错,不再出现"清理 N 个文件失败"的批量噪音。
        try:
            shutil.rmtree(OUT_DIR)
            os.makedirs(OUT_DIR, exist_ok=True)
            print("[run_all] 全部通过,已清理 output/ 产物(--keep-output 可保留)")
        except OSError as e:
            print(f"[run_all] 全部通过,清理失败: {e}")
            print(f"         可手动删除 {OUT_DIR},或用 --keep-output 保留产物")

    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    sys.exit(main())
