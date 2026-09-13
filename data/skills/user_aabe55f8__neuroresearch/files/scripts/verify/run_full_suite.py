"""一键回归脚本：批量跑 verify_*.py,输出 PASS/FAIL 表格与总耗时。

v2.3.1 新增（替代手工 `for f in verify*.py; do $PY "$f"; done`）。

用法
----
$ python verify_full_suite.py           # 默认目录 = 当前脚本所在目录
$ python verify_full_suite.py /path/to  # 自定义目录
$ python verify_full_suite.py --json    # 输出 JSON 代替 Markdown（CI 用）

行为
----
- 找目录下所有 verify*.py 与 test*.py
- 顺序跑,捕获 stdout/stderr 末 5 行
- 总耗时、exit code 0/1
- 打印 Markdown 表格("脚本名 | 状态 | 耗时 | 错误")
- 返回 exit code:全 PASS → 0,有 FAIL → 1
"""
import argparse, json, subprocess, sys, time, pathlib


def run_one(py: str, script: pathlib.Path) -> dict:
    t0 = time.perf_counter()
    try:
        proc = subprocess.run(
            [py, str(script)],
            capture_output=True, text=True, timeout=300,
        )
        dt = time.perf_counter() - t0
        return {
            "script": script.name,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "exit_code": proc.returncode,
            "elapsed_sec": round(dt, 2),
            "stdout_tail": "\n".join(proc.stdout.splitlines()[-5:]),
            "stderr_tail": "\n".join(proc.stderr.splitlines()[-5:]) if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "script": script.name,
            "status": "TIMEOUT",
            "exit_code": -1,
            "elapsed_sec": 300.0,
            "stdout_tail": "(timeout after 300s)",
            "stderr_tail": "",
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?", default=".",
                    help="verify 目录 (default: 当前目录)")
    ap.add_argument("--json", action="store_true", help="输出 JSON 报告")
    ap.add_argument("--py", default=sys.executable,
                    help="Python 解释器 (default: 当前 sys.executable)")
    args = ap.parse_args()

    here = pathlib.Path(args.dir).resolve()
    scripts = sorted(
        list(here.glob("verify*.py")) + list(here.glob("test*.py"))
    )
    # 排除自身
    scripts = [s for s in scripts if s.name != pathlib.Path(__file__).name]

    if not scripts:
        print(f"[ERROR] 在 {here} 找不到任何 verify*.py / test*.py")
        sys.exit(2)

    print(f"[Suite] {len(scripts)} 个脚本,目录={here}")
    print(f"[Suite] 解释器={args.py}\n")

    results = [run_one(args.py, s) for s in scripts]

    total = sum(r["elapsed_sec"] for r in results)
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")

    if args.json:
        print(json.dumps({
            "total": total, "pass": n_pass, "fail": n_fail,
            "scripts": results,
        }, indent=2, ensure_ascii=False))
    else:
        # Markdown 表格
        print("| 脚本 | 状态 | 退出码 | 耗时 | 末尾输出 |")
        print("|---|---|---|---|---|")
        for r in results:
            tail = r["stdout_tail"].replace("|", r"\|").replace("\n", " ⏎ ")
            tail = tail[:120] + ("..." if len(tail) > 120 else "")
            print(f"| {r['script']} | "
                  f"**{r['status']}** | {r['exit_code']} | "
                  f"{r['elapsed_sec']}s | `{tail}` |")
        print(f"\n**结果**: {n_pass}/{len(results)} PASS, "
              f"{n_fail} FAIL, 总耗时 {total:.1f}s")

    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
