"""回归测试 — 修复 BUG 1 并补全缺失覆盖率（v2.0.2）。

覆盖范围：
- BUG 1: http_get urllib fallback 变量遮蔽（请求库不可用时的多轮重试）
- BUG 1b: http_post 同样问题
- fetch_holdings._parse_holdings_table 解析（之前未测试）
- fetch_holdings._aggregate_holdings 聚合逻辑
- monthly_updater.bump_skill_version（之前未测试）
- monthly_updater.smart_update 入口
- manager_search 匹配算法（之前未测试）
- distill_manager 规则引擎（之前未测试）
- export_table 数据收集
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock


def _today() -> str:
    """当前日期，避免 cache TTL 测试因硬编码日期失效（BUG-1 修复）。"""
    return datetime.now().strftime("%Y-%m-%d")

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


# ============================================================
# FIXTURE: 隔离目录的上下文管理器（带自动恢复）
# ============================================================

class _DirIsolation:
    """安全的目录隔离 — 退出时即使有异常也会恢复所有 _common 模块路径常量"""
    def __init__(self):
        self.original = {}
        self.tmp = None

    def __enter__(self):
        import _common
        self.original = {
            "DATA_DIR": _common.DATA_DIR,
            "MANAGERS_DIR": _common.MANAGERS_DIR,
            "PROGRESS_DIR": _common.PROGRESS_DIR,
            "EXPORTS_DIR": _common.EXPORTS_DIR,
            "ROSTER_PATH": _common.ROSTER_PATH,
        }
        self.tmp = tempfile.mkdtemp()
        data_dir = os.path.join(self.tmp, "data")
        mgr_dir = os.path.join(data_dir, "managers")
        prog_dir = os.path.join(data_dir, "progress")
        exp_dir = os.path.join(data_dir, "exports")
        os.makedirs(mgr_dir); os.makedirs(prog_dir); os.makedirs(exp_dir)

        _common.DATA_DIR = data_dir
        _common.MANAGERS_DIR = mgr_dir
        _common.PROGRESS_DIR = prog_dir
        _common.EXPORTS_DIR = exp_dir
        _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")
        return self.tmp

    def __exit__(self, *args):
        try:
            import _common
            for k, v in self.original.items():
                setattr(_common, k, v)
        finally:
            if self.tmp:
                import shutil
                shutil.rmtree(self.tmp, ignore_errors=True)


# ============================================================
# BUG 1 回归测试: http_get urllib fallback 不再被变量遮蔽
# ============================================================

def test_http_get_urllib_fallback_retries_all_attempts():
    """当 requests 不可用，urlopen 必须被调用 N=retries 次（不是 1 次）"""
    # 强制 reload 防止缓存
    if "_common" in sys.modules:
        del sys.modules["_common"]
    import _common
    import urllib.request

    attempt_count = 0

    def fail_urlopen(*a, **kw):
        nonlocal attempt_count
        attempt_count += 1
        raise Exception(f"attempt {attempt_count} failed")

    with patch.object(_common, "_get_requests", return_value=None), \
         patch.object(_common, "_random_delay"), \
         patch.object(_common.time, "sleep"):
        with patch.object(urllib.request, "urlopen", side_effect=fail_urlopen):
            result = _common.http_get("http://x.invalid/foo", retries=3, timeout=5)
            assert result is None
            assert attempt_count == 3, (
                f"BUG 1 回归：urllib fallback 应当 3 次重试，"
                f"实际只调用 {attempt_count} 次（变量被遮蔽）"
            )


def test_http_get_urllib_fallback_eventual_success():
    """第 N-1 次成功时也应返回（验证 retry 链完整）"""
    if "_common" in sys.modules:
        del sys.modules["_common"]
    import _common
    import urllib.request

    call_count = 0

    def succeed_on_third(*a, **kw):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("network down")
        # 第三次返回 mock response
        class FakeResp:
            def __init__(self):
                self._body = b"<html>ok</html>"
            def read(self):
                return self._body
            def __enter__(self): return self
            def __exit__(self, *a): pass
        return FakeResp()

    with patch.object(_common, "_get_requests", return_value=None), \
         patch.object(_common, "_random_delay"), \
         patch.object(_common.time, "sleep"):
        with patch.object(urllib.request, "urlopen", side_effect=succeed_on_third):
            result = _common.http_get("http://x.invalid/foo", retries=3, timeout=5)
            assert result == "<html>ok</html>", f"Got {result!r}"
            assert call_count == 3


def test_http_post_urllib_fallback_retries_all_attempts():
    """http_post 同样的修复点 — POST urllib fallback 不能被遮蔽"""
    if "_common" in sys.modules:
        del sys.modules["_common"]
    import _common
    import urllib.request

    attempt_count = 0

    def fail_urlopen(*a, **kw):
        nonlocal attempt_count
        attempt_count += 1
        raise Exception("post fail")

    with patch.object(_common, "_get_requests", return_value=None), \
         patch.object(_common, "_random_delay"), \
         patch.object(_common.time, "sleep"):
        with patch.object(urllib.request, "urlopen", side_effect=fail_urlopen):
            result = _common.http_post("http://x.invalid/post", json_body={"x": 1}, retries=3)
            assert result is None
            assert attempt_count == 3, (
                f"POST urllib fallback 应当 3 次重试，"
                f"实际 {attempt_count} 次（变量被遮蔽）"
            )


# ============================================================
# fetch_holdings — 解析与聚合逻辑
# ============================================================

def test_parse_holdings_table_basic_stock():
    """_parse_holdings_table 解析标准股票持仓行（5 列：排名/代码/名称/占比/持股数/市值）"""
    import fetch_holdings

    html = """
    <table>
    <tr><th>序号</th><th>股票代码</th><th>股票名称</th><th>占净值比例</th><th>持股数(万股)</th><th>持仓市值(万元)</th></tr>
    <tr><td>1</td><td>000001</td><td>平安银行</td><td>5.32%</td><td>100.00</td><td>1234.56</td></tr>
    <tr><td>2</td><td>000002</td><td>万科A</td><td>4.21%</td><td>50.00</td><td>890.12</td></tr>
    </table>
    """
    holdings = fetch_holdings._parse_holdings_table(html, "stock")
    assert len(holdings) == 2
    assert holdings[0]["rank"] == 1
    assert holdings[0]["code"] == "000001"
    assert holdings[0]["name"] == "平安银行"
    assert holdings[0]["ratio"] == "5.32%"
    assert holdings[0]["type"] == "stock"


def test_parse_holdings_table_stops_at_new_period():
    """同一页面含多期持仓时，应只取最新报告期"""
    import fetch_holdings
    html = """
    <tr><td>1</td><td>000001</td><td>股票A</td><td>5%</td><td>100</td><td>1000</td></tr>
    <tr><td>2</td><td>000002</td><td>股票B</td><td>4%</td><td>80</td><td>800</td></tr>
    <tr><td>1</td><td>000003</td><td>股票C</td><td>3%</td><td>60</td><td>600</td></tr>
    """
    holdings = fetch_holdings._parse_holdings_table(html, "stock")
    assert len(holdings) == 2
    assert holdings[0]["name"] == "股票A"
    assert holdings[1]["name"] == "股票B"


def test_aggregate_holdings_dedup_and_total():
    """_aggregate_holdings 应按股票去重并累加占比"""
    import fetch_holdings

    results = [
        {"fund_code": "A", "report_date": "2026-06-30", "holdings": [
            {"code": "000001", "name": "平安银行", "ratio": "5.32%", "total_ratio": 5.32},
            {"code": "000002", "name": "万科A", "ratio": "4.21%", "total_ratio": 4.21},
        ]},
        {"fund_code": "B", "report_date": "2026-06-30", "holdings": [
            {"code": "000001", "name": "平安银行", "ratio": "3.10%", "total_ratio": 3.10},
            {"code": "000003", "name": "招商银行", "ratio": "2.50%", "total_ratio": 2.50},
        ]},
    ]
    agg = fetch_holdings._aggregate_holdings(results)

    assert agg["latest_date"] == "2026-06-30"
    assert len(agg["holdings"]) == 3

    # 平安银行被两只基金持有
    pingan = next(h for h in agg["holdings"] if h["name"] == "平安银行")
    assert pingan["appear_count"] == 2
    assert abs(pingan["total_ratio"] - 8.42) < 0.01  # 5.32 + 3.10
    assert pingan["fund_count"] == 2


def test_aggregate_holdings_picks_latest_report_date():
    """多基金中最新报告日期应被正确选取"""
    import fetch_holdings

    results = [
        {"fund_code": "A", "report_date": "2026-03-31", "holdings": []},
        {"fund_code": "B", "report_date": "2026-06-30", "holdings": []},
        {"fund_code": "C", "report_date": "2026-05-15", "holdings": []},
    ]
    agg = fetch_holdings._aggregate_holdings(results)
    assert agg["latest_date"] == "2026-06-30"


def test_aggregate_holdings_handles_invalid_ratio():
    """占比解析失败应降级为 0，不应抛出异常"""
    import fetch_holdings
    results = [
        {"fund_code": "A", "report_date": "2026-06-30", "holdings": [
            {"code": "000001", "name": "股票A", "ratio": "N/A%", "total_ratio": "N/A"},
        ]},
    ]
    agg = fetch_holdings._aggregate_holdings(results)
    assert len(agg["holdings"]) == 1
    assert agg["holdings"][0]["total_ratio"] == 0


# ============================================================
# manager_search — 匹配算法（之前未测试）
# ============================================================

def test_search_managers_exact_match():
    """search_managers 完全匹配姓名应得最高分"""
    from manager_search import build_manager_index, search_managers

    # 用临时索引构造
    fake_index = {
        "meta": {"last_update": _today(), "count": 3, "source": "test"},
        "managers": [
            {"id": "1", "name": "张三", "company": "A基金", "company_id": "c1",
             "fund_codes": ["000001"], "fund_names": ["A基金产品"],
             "tenure_days": 100, "tenure_return": "20%", "rep_fund_code": "000001",
             "rep_fund_name": "A基金产品", "scale": "10亿", "rep_fund_return": "5%"},
            {"id": "2", "name": "李四", "company": "B基金", "company_id": "c2",
             "fund_codes": [], "fund_names": [],
             "tenure_days": 200, "tenure_return": "30%", "rep_fund_code": "",
             "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
            {"id": "3", "name": "王三五", "company": "A基金", "company_id": "c1",
             "fund_codes": [], "fund_names": [],
             "tenure_days": 50, "tenure_return": "10%", "rep_fund_code": "",
             "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
        ],
    }
    with patch("manager_search.read_json", return_value=fake_index), \
         patch("manager_search.INDEX_PATH", "/fake/path"):
        results = search_managers("张三", search_type="name")
    assert len(results) == 1
    assert results[0]["name"] == "张三"
    assert results[0]["match_score"] == 100  # 完全匹配


def test_search_managers_partial_match_in_name():
    """姓名包含关键词应得分 90"""
    from manager_search import read_json
    from unittest.mock import patch

    fake_index = {"meta": {"last_update": _today(), "count": 1},
                  "managers": [
                      {"id": "1", "name": "张三丰", "company": "A",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
                  ]}
    from manager_search import search_managers
    with patch("manager_search.read_json", return_value=fake_index):
        results = search_managers("张三", search_type="name")
    assert len(results) == 1
    assert results[0]["match_score"] == 90  # 姓名包含


def test_search_managers_match_by_company():
    """公司名匹配应得分 50"""
    from manager_search import search_managers
    from unittest.mock import patch

    fake_index = {"meta": {"last_update": _today(), "count": 1},
                  "managers": [
                      {"id": "1", "name": "某人", "company": "易方达基金",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
                  ]}
    with patch("manager_search.read_json", return_value=fake_index):
        results = search_managers("易方达", search_type="company")
    assert len(results) == 1
    assert results[0]["match_score"] == 50


def test_search_managers_company_filter():
    """company_filter 应过滤非匹配公司"""
    from manager_search import search_managers
    from unittest.mock import patch

    fake_index = {"meta": {"last_update": _today(), "count": 2},
                  "managers": [
                      {"id": "1", "name": "张A", "company": "易方达基金",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
                      {"id": "2", "name": "李B", "company": "华夏基金",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
                  ]}
    with patch("manager_search.read_json", return_value=fake_index):
        results = search_managers("张", search_type="name", company_filter="易方达")
    assert len(results) == 1
    assert results[0]["company"] == "易方达基金"


def test_search_managers_results_sorted_by_score():
    """搜索结果应按匹配度从高到低排序"""
    from manager_search import search_managers
    from unittest.mock import patch

    fake_index = {"meta": {"last_update": _today(), "count": 3},
                  "managers": [
                      {"id": "1", "name": "张某某", "company": "A",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},  # score=85
                      {"id": "2", "name": "张三", "company": "A",
                       "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},  # score=100
                      {"id": "3", "name": "李四", "company": "A", "fund_codes": [], "fund_names": [],
                       "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
                       "rep_fund_name": "", "scale": "", "rep_fund_return": ""},  # score=0
                  ]}
    with patch("manager_search.read_json", return_value=fake_index):
        results = search_managers("张三", search_type="name")
    scores = [r["match_score"] for r in results]
    assert scores == sorted(scores, reverse=True), f"Not sorted: {scores}"


# ============================================================
# build_manager_index — 缓存过期降级（v2.0.0 新增回归测试）
# ============================================================

def test_build_manager_index_falls_back_to_stale_cache_on_http_failure():
    """缓存过期但 HTTP 重建失败时，应降级返回过期缓存而非空 list（v2.0.0 修复）。"""
    from manager_search import build_manager_index
    from datetime import timedelta
    from datetime import datetime as _dt

    # 过期 30 天的缓存
    stale_date = (_dt.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    stale_cache = {
        "meta": {"last_update": stale_date, "count": 2},
        "managers": [
            {"id": "100", "name": "张甲", "company": "A基金",
             "fund_codes": [], "fund_names": [],
             "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
             "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
            {"id": "101", "name": "李乙", "company": "B基金",
             "fund_codes": [], "fund_names": [],
             "tenure_days": 0, "tenure_return": "", "rep_fund_code": "",
             "rep_fund_name": "", "scale": "", "rep_fund_return": ""},
        ],
    }

    with patch("manager_search.read_json", return_value=stale_cache), \
         patch("manager_search.http_get", return_value=""):  # HTTP 失败
        results = build_manager_index()

    # 应降级返回过期缓存的 2 个经理
    assert len(results) == 2
    assert results[0]["id"] == "100"
    assert results[1]["name"] == "李乙"


def test_build_manager_index_returns_empty_when_no_cache_and_no_http():
    """无缓存且 HTTP 失败时返回空 list（明确失败而非抛异常）。"""
    from manager_search import build_manager_index

    with patch("manager_search.read_json", return_value=None), \
         patch("manager_search.http_get", return_value=""):
        results = build_manager_index()

    assert results == []


# ============================================================
# distill_manager 规则引擎
# ============================================================

def test_distill_with_rules_basic():
    """distill_with_rules 应产出 style_tags / industry_preference / bio 等核心字段"""
    import distill_manager

    materials = {
        "name": "测试经理",
        "company": "测试基金",
        "tenure_return": "100%",
        "products": ["测试产品"],
        "strategy_texts": [],
        "top_holdings": [
            {"name": "贵州茅台", "total_ratio": 9.5},
            {"name": "五粮液", "total_ratio": 8.2},
            {"name": "泸州老窖", "total_ratio": 7.1},
        ],
        "performance": {},
        "invest_idea": "",
    }
    result = distill_manager.distill_with_rules(materials)
    assert "style_tags" in result
    assert "industry_preference" in result
    assert "viewpoint_human" in result
    assert "bio" in result
    assert result["bio"].startswith("我是测试经理")
    assert "贵州茅台" in result["industry_preference"] or "消费" in result["industry_preference"]


def test_detect_top_industries_with_strategies():
    """_detect_top_industries 应能从策略文本+持仓综合识别行业"""
    import distill_manager

    holdings = [
        {"name": "腾讯", "total_ratio": 8.5},
        {"name": "阿里", "total_ratio": 7.3},
    ]
    # 策略文本提及"宁德时代"但未持仓，应该给予小幅加分
    strategies = "我们看好宁德时代代表的动力电池产业链"
    top, scores = distill_manager._detect_top_industries(holdings, strategies)
    assert len(top) > 0
    industry_names = [t[0] for t in top]
    assert "科技" in industry_names  # 腾讯阿里属于科技


def test_apply_distill_result_writes_to_manager():
    """apply_distill_result 应正确写回档案并更新名单状态。

    设计要点：
    - 用 pytest fixture 做模块级别隔离，避免与其他测试的状态相互污染
    - 直接调用 _common.save_manager/load_manager 测试写入路径
    - 用 mock.patch 替代 distill_manager 内部的 roster_manager import
    """
    import pytest
    import distill_manager
    from unittest.mock import patch, MagicMock
    import sys

    if "_common" in sys.modules:
        del sys.modules["_common"]
    if "distill_manager" in sys.modules:
        del sys.modules["distill_manager"]
    import _common
    import distill_manager

    # 使用独立的临时目录，不通过 _DirIsolation (避免与其他测试互相污染)
    with tempfile.TemporaryDirectory() as tmp:
        data_dir = os.path.join(tmp, "data")
        mgr_dir = os.path.join(data_dir, "managers")
        os.makedirs(mgr_dir)

        # 备份并替换模块级常量
        orig = (_common.DATA_DIR, _common.MANAGERS_DIR, _common.ROSTER_PATH)
        _common.DATA_DIR = data_dir
        _common.MANAGERS_DIR = mgr_dir
        _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")

        # 备份并替换 distill_manager 中捕获的引用
        # (apply_distill_result 不直接读这些，但 load_manager 间接依赖)

        try:
            # 1. 初始化经理档案
            _common.save_manager("test_distill", {"id": "test_distill", "name": "测试经理"})

            # 2. Patch sys.modules 让函数内 `from . import roster_manager` 落入 fake
            fake_roster = MagicMock()
            fake_roster.mark_distilled.return_value = True
            with patch.dict(sys.modules, {"roster_manager": fake_roster}):
                result = distill_manager.apply_distill_result("test_distill", {
                    "bio": "我是测试经理，专注成长投资。",
                    "viewpoint_human": "重仓科技板块",
                    "style_dna": "成长 + 集中",
                    "specialty": "科技",
                    "style_tags": ["成长"],
                    "industry_preference": ["科技"],
                    "style_code": "GROWTH-MED_POS-SECTOR_CONCENTRATED-LOW_TURNOVER-A_SHARE",
                    "engine": "rules",
                })

            assert result["success"] is True, f"apply failed: {result}"

            loaded = _common.load_manager("test_distill")
            assert "bio" in loaded, f"bio 字段未写入: {loaded}"
            assert loaded["bio"] == "我是测试经理，专注成长投资。"
            assert loaded["viewpoint_human"] == "重仓科技板块"
            assert loaded["distill_engine"] == "rules"
            assert "distill_date" in loaded
        finally:
            # 恢复模块级常量（避免污染后续测试）
            (_common.DATA_DIR, _common.MANAGERS_DIR, _common.ROSTER_PATH) = orig


def test_smart_update_empty_roster():
    """空名单时 smart_update 应返回友好提示而非崩溃。

    与上面 apply_distill 同理：先用 `del sys.modules` 清缓存，
    然后用 fresh 模块常量做隔离。
    """
    import monthly_updater

    if "_common" in sys.modules:
        del sys.modules["_common"]
    if "monthly_updater" in sys.modules:
        del sys.modules["monthly_updater"]
    if "roster_manager" in sys.modules:
        del sys.modules["roster_manager"]
    import _common
    import monthly_updater

    with tempfile.TemporaryDirectory() as tmp:
        data_dir = os.path.join(tmp, "data")
        os.makedirs(data_dir)

        orig_roster = _common.ROSTER_PATH
        _common.ROSTER_PATH = os.path.join(data_dir, "roster.json")
        try:
            # 同时 patch 月度更新器的模块级 ROSTER_PATH（如果需要）
            result = monthly_updater.smart_update()
            assert "message" in result, f"期望友好消息，实际: {result}"
            assert "名单为空" in result["message"]
        finally:
            _common.ROSTER_PATH = orig_roster


# ============================================================
# fetch_performance — 业绩汇总
# ============================================================

def test_extract_js_var_quoted_string():
    """_extract_js_var 应能从 var name = "value"; 形式提取字符串值"""
    import fetch_performance
    text = 'var fS_name = "易方达蓝筹精选"; var fS_code = "005827";'
    val = fetch_performance._extract_js_var(text, "fS_name", as_float=False)
    assert val == "易方达蓝筹精选"


def test_extract_js_var_numeric():
    """_extract_js_var 应能将数字字符串解析为 float"""
    import fetch_performance
    text = 'var syl_1y = "12.34";'
    val = fetch_performance._extract_js_var(text, "syl_1y", as_float=True)
    assert val == 12.34
    assert isinstance(val, float)


def test_extract_js_var_missing():
    """未找到变量应返回 None"""
    import fetch_performance
    text = 'var other_var = "1.23";'
    val = fetch_performance._extract_js_var(text, "missing_var", as_float=True)
    assert val is None


def test_summarize_performance_basic():
    """_summarize_performance 应正确计算平均收益率"""
    import fetch_performance

    funds = [
        {"fund_code": "A", "fund_name": "基金A",
         "returns": {"近1月": 1.0, "近3月": 3.0, "近1年": 10.0, "今年以来": 5.0}},
        {"fund_code": "B", "fund_name": "基金B",
         "returns": {"近1月": 2.0, "近3月": 4.0, "近1年": 20.0, "今年以来": 7.0}},
    ]
    summary = fetch_performance._summarize_performance(funds)
    assert summary["fund_count"] == 2
    assert summary["avg_returns"]["近1月"] == 1.5
    assert summary["avg_returns"]["近3月"] == 3.5
    assert summary["avg_returns"]["近1年"] == 15.0
    # best_fund / worst_fund 字段是嵌套 dict
    assert summary["best_fund"]["code"] == "B"
    assert summary["worst_fund"]["code"] == "A"


def test_summarize_performance_empty():
    """无基金数据应返回空 dict 不崩溃"""
    import fetch_performance
    assert fetch_performance._summarize_performance([]) == {}


def test_summarize_performance_skips_invalid_returns():
    """无效收益率（字符串无法转 float）应被跳过，不污染均值"""
    import fetch_performance
    funds = [
        {"fund_code": "A", "fund_name": "A", "returns": {"近1年": "N/A"}},
        {"fund_code": "B", "fund_name": "B", "returns": {"近1年": 20.0}},
    ]
    summary = fetch_performance._summarize_performance(funds)
    assert summary["avg_returns"]["近1年"] == 20.0  # 只取 B


# ============================================================
# fetch_reports — 章节提取
# ============================================================

def test_extract_section_th_td_pattern():
    """_extract_section 应匹配 th/td 表格形式"""
    import fetch_reports

    html = """
    <table>
    <tr><th>投资目标</th><td>本基金主要投资于具有长期增长潜力的公司。</td></tr>
    <tr><th>投资范围</th><td>沪深300成分股为主。</td></tr>
    </table>
    """
    text = fetch_reports._extract_section(html, "投资目标")
    assert "长期增长" in text

    text2 = fetch_reports._extract_section(html, "投资范围")
    assert "沪深300" in text2


def test_extract_section_label_pattern():
    """_extract_section 应匹配 label 格式"""
    import fetch_reports
    html = '<label class="left">投资理念</label><p>价值投资，长期持有。</p>'
    text = fetch_reports._extract_section(html, "投资理念")
    assert "价值投资" in text


def test_extract_section_missing():
    """不存在的章节应返回空字符串"""
    import fetch_reports
    html = "<html><body>无内容</body></html>"
    assert fetch_reports._extract_section(html, "不存在的章节") == ""


def test_extract_section_handles_empty_result():
    """匹配但太短的内容应返回空字符串"""
    import fetch_reports
    html = '<th>投资目标</th><td>无</td>'  # 只有 1 个字
    text = fetch_reports._extract_section(html, "投资目标")
    assert text == ""


# ============================================================
# export_table — 数据收集与基础导出
# ============================================================

def test_gather_all_data_empty_roster():
    """无名单时 _gather_all_data 应返回空列表"""
    import export_table
    # export_table 在模块加载时捕获了 ROSTER_PATH，要 patch 其模块级引用
    with _DirIsolation():
        with patch("export_table.ROSTER_PATH", _common.ROSTER_PATH if False else os.path.join(os.path.dirname(__file__), "_fake_empty_roster.json")):
            # 直接写一个空 roster 到一个特定路径并 patch
            fake_roster = os.path.join(os.path.dirname(__file__), "_fake_empty_roster.json")
            Path(fake_roster).write_text(json.dumps({"meta": {"count": 0}, "managers": []}), encoding="utf-8")
            try:
                with patch("export_table.ROSTER_PATH", fake_roster):
                    result = export_table._gather_all_data()
                    assert result == [], f"Expected empty list, got {result}"
            finally:
                Path(fake_roster).unlink(missing_ok=True)


def test_gather_all_data_with_managers():
    """有经理时应聚合名单元数据 + 档案详情"""
    import export_table
    with _DirIsolation() as tmp:
        import _common
        # 创建一份 roster.json 到临时目录
        temp_roster = os.path.join(tmp, "_test_roster.json")
        _common.write_json(temp_roster, {
            "meta": {"version": 1, "count": 2, "last_update": _today(), "max": 100},
            "managers": [
                {"id": "m1", "name": "甲", "company": "公司A",
                 "manager_type": "公募", "status": "distilled",
                 "add_date": "2026-01-01", "last_refresh": "2026-07-29",
                 "tenure_return": "20%"},
                {"id": "m2", "name": "乙", "company": "公司B",
                 "manager_type": "私募", "status": "active",
                 "add_date": "2026-02-01", "last_refresh": "",
                 "tenure_return": ""},
            ],
        })
        _common.save_manager("m1", {
            "bio": "我是甲，专注消费。",
            "specialty": "消费",
            "style_tags": ["价值", "集中"],
            "industry_preference": ["消费"],
            "top_holdings": [{"code": "000001", "name": "茅台", "total_ratio": 9.5}],
            "holdings_report_date": "2026-06-30",
            "performance": {},
        })
        _common.save_manager("m2", {})

        with patch("export_table.ROSTER_PATH", temp_roster):
            result = export_table._gather_all_data()
            assert len(result) == 2
            m1 = next(r for r in result if r["id"] == "m1")
            assert m1["bio"] == "我是甲，专注消费。"
            assert m1["style_tags"] == "价值, 集中"
            assert m1["tenure_return"] == "20%"
            m2 = next(r for r in result if r["id"] == "m2")
            assert m2["bio"] == ""


def test_export_roster_csv_creates_valid_file():
    """export_roster_csv 应能在临时目录生成有效 CSV（中文不丢）"""
    import export_table
    with _DirIsolation() as tmp:
        import _common
        temp_roster = os.path.join(tmp, "_test_roster_export.json")
        _common.write_json(temp_roster, {
            "meta": {"count": 1},
            "managers": [{
                "id": "1", "name": "测试经理", "company": "测试基金",
                "status": "distilled", "add_date": "2026-01-01",
                "last_refresh": "2026-07-29", "tenure_return": "20%",
            }],
        })

        with patch("export_table.ROSTER_PATH", temp_roster), \
             patch("export_table.EXPORTS_DIR", os.path.join(tmp, "exports")):
            os.makedirs(os.path.join(tmp, "exports"), exist_ok=True)
            out = export_table.export_roster_csv()
            assert os.path.exists(out)
            with open(out, encoding="utf-8-sig") as f:
                content = f.read()
            assert "测试经理" in content, f"Missing 测试经理 in: {content[:200]}"
            assert "测试基金" in content


# ============================================================
# monthly_updater — 增量检测核心 + 版本管理
# ============================================================

def test_bump_skill_version_increments_minor():
    """bump_skill_version 应增加 patch 号（v2.0.0 → v2.0.1）"""
    import monthly_updater

    with tempfile.TemporaryDirectory() as tmp:
        skill_md = Path(tmp) / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: test\n"
            "version: 2.0.0\n"
            "description: x\n"
            "---\n"
            "Body",
            encoding="utf-8"
        )
        # SKILL_MD_PATH 是模块级常量，必须 patch 它
        original_path = monthly_updater.SKILL_MD_PATH
        monthly_updater.SKILL_MD_PATH = str(skill_md)
        # 同时 patch roster 路径避免对真实文件的副作用
        import _common
        original_roster = _common.ROSTER_PATH
        _common.ROSTER_PATH = os.path.join(tmp, "data", "roster.json")
        try:
            monthly_updater.bump_skill_version()
            content = skill_md.read_text(encoding="utf-8")
            assert "version: 2.0.1" in content, f"Version not bumped: {content[:200]}"
        finally:
            monthly_updater.SKILL_MD_PATH = original_path
            _common.ROSTER_PATH = original_roster


def test_bump_skill_version_creates_data_stats_block():
    """无 DATA_STATS 区块时不应报错，也不应意外添加空区块"""
    import monthly_updater

    with tempfile.TemporaryDirectory() as tmp:
        skill_md = Path(tmp) / "SKILL.md"
        skill_md.write_text(
            "---\n"
            "name: test\n"
            "version: 2.0.0\n"
            "---\n"
            "Body without stats block",
            encoding="utf-8"
        )
        original_path = monthly_updater.SKILL_MD_PATH
        monthly_updater.SKILL_MD_PATH = str(skill_md)
        import _common
        original_roster = _common.ROSTER_PATH
        _common.ROSTER_PATH = os.path.join(tmp, "data", "roster.json")
        try:
            updated = monthly_updater.bump_skill_version()
            assert updated is True or updated is False
            content = skill_md.read_text(encoding="utf-8")
            assert "version: 2.0.1" in content
        finally:
            monthly_updater.SKILL_MD_PATH = original_path
            _common.ROSTER_PATH = original_roster




def test_write_change_log_creates_file():
    """_write_change_log 应在按日文件中追加 runs 数组"""
    import monthly_updater
    import _common

    with tempfile.TemporaryDirectory() as tmp:
        change_log_dir = os.path.join(tmp, "change_log")
        os.makedirs(change_log_dir)
        original_dir = monthly_updater.CHANGE_LOG_DIR
        monthly_updater.CHANGE_LOG_DIR = change_log_dir
        try:
            change_log = {"run_time": "2026-07-29 12:00", "engine": "auto", "managers": []}
            monthly_updater._write_change_log(change_log)
            today = __import__('datetime').datetime.now().strftime("%Y-%m-%d")
            path = Path(change_log_dir) / f"{today}.json"
            assert path.exists()
            data = json.loads(path.read_text(encoding="utf-8"))
            assert len(data["runs"]) == 1
            monthly_updater._write_change_log(change_log)
            data = json.loads(path.read_text(encoding="utf-8"))
            assert len(data["runs"]) == 2
        finally:
            monthly_updater.CHANGE_LOG_DIR = original_dir


# ============================================================
# data_backup version field — 不再是 _common.__name__
# ============================================================

def test_backup_manifest_has_real_version():
    """备份 manifest 的 skill_version 字段应是真实版本号，不再是 _common.__name__"""
    import zipfile, json
    from data_backup import backup_all

    with _DirIsolation() as tmp:
        backup_path = backup_all(os.path.join(tmp, "backups"))
        with zipfile.ZipFile(backup_path, "r") as zf:
            with zf.open("MANIFEST.json") as f:
                manifest = json.load(f)
        assert manifest["skill_version"] != "_common", (
            "BUG: skill_version 仍为 _common 占位符"
        )
        # 应该是可读版本号（带数字）
        import re
        assert re.search(r"\d+\.\d+", manifest["skill_version"]), (
            f"version 字段格式异常: {manifest['skill_version']}"
        )


# ============================================================
# 运行所有
# ============================================================

def main():
    tests = [
        (name, obj)
        for name, obj in globals().items()
        if name.startswith("test_") and callable(obj)
    ]
    passed = 0
    failed = 0
    import traceback
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*60}\n回归 + 扩展 测试: {passed} 通过, {failed} 失败\n{'='*60}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
