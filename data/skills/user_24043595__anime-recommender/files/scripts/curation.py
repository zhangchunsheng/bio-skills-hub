# -*- coding: utf-8 -*-
"""作品库治理层 · 争议/敏感作品黑名单（面向中国用户）

设计目标
--------
避免向用户推荐「在国内有明确争议、已下架/抵制」的作品。本文件是唯一的
争议拦截点，由 works_pool.pool_query 在候选收集阶段调用 is_blocked()，
因此默认片单 / 反馈重推 / 相邻补位等所有推荐路径都会自动生效。

匹配方式
--------
对作品名做「去空白 + 小写」归一化后，与 DENY_TOKENS 做子串匹配；
命中任一 token 即判定为应屏蔽作品（自动覆盖其所有语言标题与衍生作）。

为什么用 token 子串而非精确名
-----------------------------
同一作品在库里常以多种语言/衍生标题并存（如「我的英雄学院」/
「仆のヒーローアカデミア 7」/「ヴィジランテ…ILLEGALS-」），
token 子串可一次性把所有形态拦下，且不会误伤无关作品。

如何扩展
--------
新增争议作品只需在 DENY_TOKENS 追加一个「专属关键词」即可
（选该作品独有、不会出现在其他作品名里的片段，例如外文原名/中文专名）。
例如以后要屏蔽另一部，追加其专属 token 即可，无需改动其它代码。
"""
import re as _re

# ----------------------------------------------------------------------------
# 种子清单
# ----------------------------------------------------------------------------
# 我的英雄学院 (My Hero Academia)
#   2020 年争议事件，国内已下架/抵制。覆盖全部语言标题与衍生：
#     中文「我的英雄学院」、日文「ヒーローアカデミア / 仆のヒーローアカデミア」、
#     英文「My Hero Academia / Hero Academia / Boku no Hero」、
#     衍生「ヴィジランテ -仆のヒーローアカデミア ILLEGALS-」。
#   注：仅用 MHA 专属 token，不会误伤其它含「英雄」二字的作品。
DENY_TOKENS = [
    "我的英雄学院",
    "ヒーローアカデミア",   # Hero Academia（片假名，MHA 专属）
    "my hero academia",
    "hero academia",
    "boku no hero",
]


def _norm(s):
    """去空白 + 小写，用于子串匹配。"""
    return _re.sub(r"\s+", "", (s or "").lower())


_NORM_TOKENS = [_norm(t) for t in DENY_TOKENS]


def is_blocked(name):
    """判断作品名是否属于争议/应屏蔽作品。命中任一 DENY token 即 True。"""
    n = _norm(name)
    if not n:
        return False
    return any(tok in n for tok in _NORM_TOKENS)


def add_deny_token(token):
    """运行时追加争议关键词（注意：仅当前进程有效，持久化需写回 DENY_TOKENS）。"""
    t = _norm(token)
    if t and t not in _NORM_TOKENS:
        DENY_TOKENS.append(token)
        _NORM_TOKENS.append(t)
        return True
    return False


if __name__ == "__main__":
    tests = [
        "我的英雄学院", "我的英雄学院 3", "仆のヒーローアカデミア 7",
        "ヴィジランテ -仆のヒーローアカデミア ILLEGALS-",
        "我的英雄学院 THE MOVIE 英雄崛起", "My Hero Academia",
        "命运石之门", "强风吹拂", "CLANNAD",
    ]
    for t in tests:
        print(f"  {t:50s} -> blocked={is_blocked(t)}")
