#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fasta_toolkit.py — 植物分子鉴定DNA条形码分析工具（纯标准库，无第三方依赖）

功能：
  stats      统计FASTA中每条序列的长度、GC含量、碱基组成
  revcomp    输出指定序列的反向互补（用于反链测序结果校正）
  align      双序列全局比对（Needleman-Wunsch）：差异位点、p距离、K2P距离、一致性%
  consensus  正反向序列拼接为consensus（IUPAC简并码合并）

用法示例：
  python3 fasta_toolkit.py stats seqs.fa
  python3 fasta_toolkit.py revcomp seqs.fa Sample01_ITS2_F
  python3 fasta_toolkit.py align fwd.fa rev.fa
  python3 fasta_toolkit.py consensus fwd.fa rev.fa

说明：
  - 仅支持标准碱基 A/T/G/C/N 与 IUPAC简并码（R,Y,S,W,K,M,B,D,H,V）
  - 非ACGT字符（N/简并码）不参与GC%计算分母时按有效碱基处理
  - 序列中空白与数字将被忽略；"*" 视为终止/缺失标记并剔除
"""

import sys
import re
import math

# ---------------------------------------------------------------------------
# IUPAC 简并码
# ---------------------------------------------------------------------------

# 简并码 -> 展开的碱基集合
IUPAC_EXPAND = {
    "A": {"A"}, "C": {"C"}, "G": {"G"}, "T": {"T"}, "U": {"T"}, "N": {"A", "C", "G", "T"},
    "R": {"A", "G"}, "Y": {"C", "T"}, "S": {"G", "C"}, "W": {"A", "T"},
    "K": {"G", "T"}, "M": {"A", "C"},
    "B": {"C", "G", "T"}, "D": {"A", "G", "T"}, "H": {"A", "C", "T"}, "V": {"A", "C", "G"},
}

# 两个碱基/简并码合并 -> 最小简并码（无公共碱基返回 None）
# 互补映射：A<->T, U->A, N->N, R<->Y, S<->S, W<->W, K<->M, B<->V, D<->H
_COMPLEMENT = str.maketrans("ACGTUNRYSWKMBDHV", "TGCAANRYSWMKVHDB")


def revcomp(seq: str) -> str:
    """反向互补（U 视为 T）。"""
    seq = seq.upper().replace("U", "T")
    return seq.translate(_COMPLEMENT)[::-1]


def merge_iupac(base_a: str, base_b: str):
    """
    合并两个位置碱基为最小IUPAC码（并集语义：正反链观测到的碱基集合）。
    例：A+G -> R（杂合A/G）；A+C -> M；R+A -> R；A+A -> A。
    碱基超出IUPAC表（无法解析）返回 None。
    """
    set_a = IUPAC_EXPAND.get(base_a.upper())
    set_b = IUPAC_EXPAND.get(base_b.upper())
    if set_a is None or set_b is None:
        return None
    union = set_a | set_b
    if len(union) == 1:
        return next(iter(union))
    for code, bases in IUPAC_EXPAND.items():
        if bases == union:
            return code
    return "N"  # 覆盖全部4种碱基


# ---------------------------------------------------------------------------
# FASTA 解析
# ---------------------------------------------------------------------------

def parse_fasta(path: str):
    """解析FASTA文件，返回 [(id, seq), ...]。序列大写、去空白。"""
    records = []
    cur_id = None
    chunks = []
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if cur_id is not None:
                    records.append((cur_id, "".join(chunks)))
                header = line[1:].strip()
                cur_id = header.split()[0] if header else "seq%d" % (len(records) + 1)
                chunks = []
            else:
                # 去空白与数字（部分FASTA含行号），剔除终止符
                cleaned = re.sub(r"[\s\d*\-]", "", line).upper()
                chunks.append(cleaned)
    if cur_id is not None:
        records.append((cur_id, "".join(chunks)))
    return records


def get_record(records, target):
    """按 id 或序号(1-based)取记录；支持模糊前缀匹配，返回 (id, seq) 或 None。"""
    for i, (rid, seq) in enumerate(records, 1):
        if rid == target or str(i) == target:
            return rid, seq
    # 前缀匹配（id 可能带注释后缀）
    for rid, seq in records:
        if rid.startswith(target):
            return rid, seq
    return None


# ---------------------------------------------------------------------------
# 统计
# ---------------------------------------------------------------------------

def stats_command(path):
    records = parse_fasta(path)
    if not records:
        print("错误：文件中没有FASTA记录")
        return 1
    print("%-28s %8s %8s %10s" % ("ID", "长度(bp)", "GC%", "含N/简并码"))
    print("-" * 62)
    for rid, seq in records:
        if not seq:
            print("%-28s %8d %8s %10s" % (rid, 0, "-", "-"))
            continue
        length = len(seq)
        atgc = sum(1 for c in seq if c in "ATGC")
        gc = sum(1 for c in seq if c in "GC")
        gc_pct = (gc / atgc * 100) if atgc else 0.0
        amb = sum(1 for c in seq if c not in "ATGC")
        print("%-28s %8d %7.2f%% %10d" % (rid, length, gc_pct, amb))
    # 汇总
    lens = [len(s) for s in (s for _, s in records) if s]
    if lens:
        print("-" * 62)
        print("序列数: %d | 长度范围: %d–%d bp | 平均: %.1f bp" % (len(records), min(lens), max(lens), sum(lens) / len(lens)))
    return 0


# ---------------------------------------------------------------------------
# 反向互补
# ---------------------------------------------------------------------------

def revcomp_command(path, target):
    records = parse_fasta(path)
    hit = get_record(records, target)
    if not hit:
        print("错误：找不到序列 '%s'。可用ID：" % target)
        for rid, _ in records:
            print("  ", rid)
        return 1
    rid, seq = hit
    rc = revcomp(seq)
    print(">%s_revcomp" % rid)
    print(rc)
    print("# 原序列长度: %d | 反向互补长度: %d" % (len(seq), len(rc)))
    return 0


# ---------------------------------------------------------------------------
# 双序列全局比对（Needleman-Wunsch）
# ---------------------------------------------------------------------------

_MATCH = 2
_MISMATCH = -1
_GAP = -2


def needleman_wunsch(seq_a, seq_b):
    """全局比对，返回 (对齐A, 对齐B, 得分)。"""
    n, m = len(seq_a), len(seq_b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i * _GAP
    for j in range(m + 1):
        dp[0][j] = j * _GAP
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            score = _MATCH if seq_a[i - 1] == seq_b[j - 1] else _MISMATCH
            dp[i][j] = max(
                dp[i - 1][j - 1] + score,
                dp[i - 1][j] + _GAP,
                dp[i][j - 1] + _GAP,
            )
    # 回溯
    aln_a, aln_b = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            score = _MATCH if seq_a[i - 1] == seq_b[j - 1] else _MISMATCH
            if dp[i][j] == dp[i - 1][j - 1] + score:
                aln_a.append(seq_a[i - 1]); aln_b.append(seq_b[j - 1])
                i -= 1; j -= 1
                continue
        if i > 0 and dp[i][j] == dp[i - 1][j] + _GAP:
            aln_a.append(seq_a[i - 1]); aln_b.append("-")
            i -= 1
        else:
            aln_a.append("-"); aln_b.append(seq_b[j - 1])
            j -= 1
    return "".join(reversed(aln_a)), "".join(reversed(aln_b)), dp[n][m]


def p_distance(aln_a, aln_b):
    """p-distance：差异位点数 / 有效比对位点数（忽略双gap列）。"""
    sites = diffs = 0
    for a, b in zip(aln_a, aln_b):
        if a == "-" and b == "-":
            continue
        sites += 1
        if a != b:
            diffs += 1
    return (diffs / sites) if sites else 0.0, diffs, sites


def k2p_distance(aln_a, aln_b):
    """K2P距离（Kimura 2-parameter）：需序列可计算转换/颠换。"""
    tv = ts = sites = 0
    purines = "AG"
    for a, b in zip(aln_a, aln_b):
        if a == "-" or b == "-" or a == b:
            if a != "-" and b != "-":
                sites += 1
            continue
        sites += 1
        if a in purines and b in purines or a not in purines and b not in purines:
            ts += 1
        else:
            tv += 1
    if sites == 0:
        return float("nan")
    p = ts / sites
    q = tv / sites
    denom = (1 - 2 * p - q)
    if denom <= 0:
        return float("inf")
    d = -0.5 * math.log(1 - 2 * p - q) - 0.5 * math.log(1 - 2 * q)
    return max(0.0, d)  # 序列几乎一致时公式可能给出微小负值，钳制为0


def align_command(path_a, path_b):
    recs_a = parse_fasta(path_a)
    recs_b = parse_fasta(path_b)
    if not recs_a or not recs_b:
        print("错误：比对需要两个非空FASTA文件")
        return 1
    if len(recs_a) > 1 or len(recs_b) > 1:
        print("提示：文件含多条序列，默认取每个文件第一条；如需指定序列请用单序列文件。")
    rid_a, seq_a = recs_a[0]
    rid_b, seq_b = recs_b[0]
    aln_a, aln_b, score = needleman_wunsch(seq_a, seq_b)
    pdist, ndiff, nsites = p_distance(aln_a, aln_b)
    k2p = k2p_distance(aln_a, aln_b)
    identical = sum(1 for a, b in zip(aln_a, aln_b) if a == b and a != "-")
    aln_len = len(aln_a)
    identity = identical / aln_len * 100 if aln_len else 0.0

    print("比对对象: %s (%d bp)  vs  %s (%d bp)" % (rid_a, len(seq_a), rid_b, len(seq_b)))
    print("比对得分(全局): %d | 比对列数: %d" % (score, aln_len))
    print("一致位点: %d (%.2f%%) | 差异位点: %d | 有效位点: %d" % (identical, identity, ndiff, nsites))
    print("p距离: %.4f | K2P距离: %s" % (pdist, "inf(不可计算,差异过大)" if k2p == float("inf") else ("%.4f" % k2p)))
    # 输出变异位点列表（1-based，按比对列）
    var_positions = []
    for i, (a, b) in enumerate(zip(aln_a, aln_b), 1):
        if a != b:
            var_positions.append((i, a, b))
    if var_positions:
        print("变异位点（比对列位置: 序列A>序列B）:")
        row = []
        for pos, a, b in var_positions:
            row.append("%d:%s>%s" % (pos, a, b))
        # 每行 5 个
        for k in range(0, len(row), 5):
            print("  " + "  ".join(row[k:k + 5]))
    else:
        print("变异位点: 无（序列完全一致）")
    print()
    print("对齐输出（每60字符一行）:")
    for k in range(0, len(aln_a), 60):
        print("  A | " + aln_a[k:k + 60])
        print("  B | " + aln_b[k:k + 60])
        print()
    return 0


# ---------------------------------------------------------------------------
# 正反向 consensus 拼接
# ---------------------------------------------------------------------------

def consensus_command(path_fwd, path_rev):
    recs_f = parse_fasta(path_fwd)
    recs_r = parse_fasta(path_rev)
    if not recs_f or not recs_r:
        print("错误：拼接需要正反向各一个FASTA文件")
        return 1
    if len(recs_f) > 1 or len(recs_r) > 1:
        print("提示：文件含多条序列，默认取每个文件第一条（正反向各一条）。")
    id_f, seq_f = recs_f[0]
    id_r, seq_r = recs_r[0]
    seq_r_rc = revcomp(seq_r)  # 反向序列先反向互补

    # 寻找重叠区：反向互补后的序列与正向序列的最长一致末端重叠
    best = None  # (overlap_len, start_in_f, start_in_r, mismatches)
    # 正向尾部 vs 反向互补头部 的重叠（常规拼接方向）
    max_ov = min(len(seq_f), len(seq_r_rc))
    min_ov = 20
    for ov in range(max_ov, min_ov - 1, -1):
        # 正向末尾 ov 个碱基 与 反向互补开头 ov 个碱基
        tail_f = seq_f[-ov:]
        head_r = seq_r_rc[:ov]
        mism = sum(1 for a, b in zip(tail_f, head_r) if a != b)
        if mism <= max(1, ov // 20):  # 允许 ≤5% 不一致（测序误差）
            best = (ov, len(seq_f) - ov, 0, mism)
            break
    if best is None:
        # 尝试正向头部 vs 反向互补尾部（测序方向相反的情况）
        for ov in range(min(len(seq_f), len(seq_r_rc)), min_ov - 1, -1):
            head_f = seq_f[:ov]
            tail_r = seq_r_rc[-ov:]
            mism = sum(1 for a, b in zip(head_f, tail_r) if a != b)
            if mism <= max(1, ov // 20):
                best = (ov, 0, len(seq_r_rc) - ov, mism)
                break
    if best is None:
        print("错误：未找到足够长的重叠区（最小%d bp）。请检查正反向序列是否来自同一PCR产物。" % min_ov)
        print("正向序列长度: %d | 反向(互补后)序列长度: %d" % (len(seq_f), len(seq_r_rc)))
        return 1

    ov, s_f, s_r, mism = best
    # 拼接：正向 5' 端 + 重叠区(合并) + 反向 3' 端
    prefix_f = seq_f[:s_f]
    overlap_f = seq_f[s_f:s_f + ov]
    overlap_r = seq_r_rc[s_r:s_r + ov]
    suffix_r = seq_r_rc[s_r + ov:]
    merged = []
    conflicts = []
    for i, (a, b) in enumerate(zip(overlap_f, overlap_r), 1):
        if a == b:
            merged.append(a)
        else:
            code = merge_iupac(a, b)
            if code:
                merged.append(code)
                conflicts.append((s_f + i, a, b, code))
            else:
                # 碱基无法解析：以正向为准，记录警告
                merged.append(a)
                conflicts.append((s_f + i, a, b, "!"))
    consensus = prefix_f + "".join(merged) + suffix_r

    print(">%s_consensus (fwd=%s / rev=%s)" % (id_f, id_f, id_r))
    for k in range(0, len(consensus), 70):
        print(consensus[k:k + 70])
    print()
    print("重叠区长度: %d bp | 重叠区不一致位点: %d" % (ov, mism))
    print("正链长度: %d | 反链(互补后): %d | consensus长度: %d" % (len(seq_f), len(seq_r_rc), len(consensus)))
    if conflicts:
        print("重叠区合并标注（位置: 正>反: 合并码）:")
        for pos, a, b, code in conflicts:
            if code == "!":
                print("  位点 %d: %s>%s → 碱基无法解析，取正向碱基 %s（请核对峰图！）" % (pos, a, b, a))
            else:
                print("  位点 %d: %s>%s → 简并码 %s（杂合位点或正反测序不一致，请核对峰图）" % (pos, a, b, code))
    else:
        print("重叠区无碱基冲突，consensus 拼接干净。")
    return 0


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd = sys.argv[1].lower()
    if cmd == "stats":
        if len(sys.argv) < 3:
            print("用法: fasta_toolkit.py stats <fasta文件>"); return 1
        return stats_command(sys.argv[2])
    if cmd == "revcomp":
        if len(sys.argv) < 4:
            print("用法: fasta_toolkit.py revcomp <fasta文件> <序列ID或序号>"); return 1
        return revcomp_command(sys.argv[2], sys.argv[3])
    if cmd == "align":
        if len(sys.argv) < 4:
            print("用法: fasta_toolkit.py align <seqA.fa> <seqB.fa>"); return 1
        return align_command(sys.argv[2], sys.argv[3])
    if cmd == "consensus":
        if len(sys.argv) < 4:
            print("用法: fasta_toolkit.py consensus <fwd.fa> <rev.fa>"); return 1
        return consensus_command(sys.argv[2], sys.argv[3])
    print("未知命令: %s（支持: stats / revcomp / align / consensus）" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
