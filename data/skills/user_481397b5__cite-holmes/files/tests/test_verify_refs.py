#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cite-holmes verify_refs.py 回归测试套件（v1.3.0 起）。

离线为主（快、稳定）；E-utilities 在线核验单列一组，网络不可达时跳过。
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import verify_refs as vr  # noqa: E402

EXAMPLES = os.path.join(HERE, "..", "examples")
DEMO = os.path.join(EXAMPLES, "demo_refs.json")
GOLDEN_OFFLINE = ["verified", "partial", "verified", "partial",
                  "partial", "verified", "verified", "invalid"]


def run_offline(refs):
    results = []
    for i, ref in enumerate(refs, 1):
        results.append(vr.verify_one(ref, i, True, 5.0))
    vr.mark_duplicates(results)
    return results


class TestOfflineBaseline(unittest.TestCase):
    """demo_refs.json（3 个埋雷 + 5 条真实）的判定金样本，自 v1.0 冻结。"""

    def test_demo_refs_golden_sequence(self):
        refs = json.load(open(DEMO, encoding="utf-8"))
        results = run_offline(refs)
        self.assertEqual([r["verdict"] for r in results], GOLDEN_OFFLINE)

    def test_scorecard_baseline(self):
        results = run_offline(json.load(open(DEMO, encoding="utf-8")))
        sc = vr.compute_scorecard(results)
        self.assertEqual(sc["counts"]["verified"], 4)
        self.assertEqual(sc["counts"]["partial"], 3)
        self.assertEqual(sc["counts"]["invalid"], 1)
        self.assertEqual(sc["score"], 55)
        self.assertEqual(sc["grade"], "C")


class TestScorecard(unittest.TestCase):
    def test_all_verified_is_100A(self):
        refs = [{"title": f"study {i}", "url": f"https://www.nature.com/p{i}",
                 "source": "journal", "year": 2025} for i in range(9)]
        sc = vr.compute_scorecard(run_offline(refs))
        self.assertEqual((sc["score"], sc["grade"]), (100, "A"))

    def test_all_invalid_is_0D(self):
        refs = [{"title": f"x{i}"} for i in range(5)]
        sc = vr.compute_scorecard(run_offline(refs))
        self.assertEqual((sc["score"], sc["grade"]), (0, "D"))

    def test_empty(self):
        sc = vr.compute_scorecard([])
        self.assertEqual(sc["score"], 0)
        self.assertEqual(sc["total"], 0)

    def test_render_md_contains_scorecard(self):
        md = vr.render_md(run_offline(json.load(open(DEMO, encoding="utf-8"))), True)
        self.assertIn("CiteScore", md)
        self.assertIn("55 / 100 · C 级", md)


class TestDedupThreeKey(unittest.TestCase):
    def test_url_doi_pmid_dedup(self):
        results = [
            {"index": 1, "title": "a", "url": "https://x.com/", "doi": "10.1000/a",
             "pmid": "36443570", "verdict": "verified", "note": ""},
            {"index": 2, "title": "b", "url": "https://x.com", "doi": "", "pmid": "",
             "verdict": "verified", "note": ""},
            {"index": 3, "title": "c", "url": "https://y.com", "doi": "10.1000/A",
             "pmid": "", "verdict": "verified", "note": ""},
            {"index": 4, "title": "d", "url": "https://z.com", "doi": "",
             "pmid": "36443570", "verdict": "verified", "note": ""},
        ]
        vr.mark_duplicates(results)
        self.assertIn("与 #1 重复（同URL）", results[1]["note"])
        self.assertIn("与 #1 重复（同DOI）", results[2]["note"])
        self.assertIn("与 #1 重复（同PMID）", results[3]["note"])
        for r in results[1:]:
            self.assertEqual(r["verdict"], "partial")
        self.assertEqual(results[0]["verdict"], "verified")


class TestMissingFields(unittest.TestCase):
    def test_doi_satisfies_url(self):
        self.assertNotIn("url", vr.missing_fields(
            {"title": "t", "source": "s", "year": 2024, "doi": "10.1000/abc"}))

    def test_pmid_satisfies_url(self):
        self.assertNotIn("url", vr.missing_fields(
            {"title": "t", "source": "s", "year": 2024, "pmid": "36443570"}))

    def test_nothing_satisfies(self):
        self.assertIn("url", vr.missing_fields(
            {"title": "t", "source": "s", "year": 2024}))


class TestMedicalProfile(unittest.TestCase):
    def test_medical_tier_expansion(self):
        # 万方：默认层为 blog，medical 预设下升入 journal 层
        url = "https://d.wanfangdata.com.cn/periodical/example"
        self.assertEqual(vr.classify_tier(url, False), "blog")
        self.assertEqual(vr.classify_tier(url, True), "journal")

    def test_medical_offline_verified(self):
        ref = {"title": "万方文献", "url": "https://d.wanfangdata.com.cn/periodical/x",
               "source": "期刊", "year": 2024}
        r = vr.verify_one(ref, 1, True, 5.0, medical=True)
        self.assertEqual(r["verdict"], "verified")

    def test_medical_community_caveat(self):
        ref = {"title": "知乎讨论", "url": "https://zhuanlan.zhihu.com/p/123",
               "source": "community", "year": 2024}
        r = vr.verify_one(ref, 1, True, 5.0, medical=True)
        self.assertIn("不得支撑医学结论", r["note"])


class TestExports(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="ch_test_")

    def _sample_results(self):
        return [
            {"index": 1, "title": "Real Study", "verdict": "verified", "tier": "journal",
             "http_status": 200, "needs_human_check": False, "year": 2023,
             "source": "Journal", "url": "https://a.b/c", "doi": "", "pmid": "36443570", "note": ""},
            {"index": 2, "title": "Fake Study", "verdict": "invalid", "tier": "-",
             "http_status": None, "needs_human_check": True, "year": 2023,
             "source": "", "url": "", "doi": "", "pmid": "99999999", "note": "编造"},
        ]

    def test_bibtex_verified_only(self):
        p = os.path.join(self.tmp, "out.bib")
        n = vr.export_bibtex(self._sample_results(), p)
        self.assertEqual(n, 1)
        content = open(p, encoding="utf-8").read()
        self.assertIn("@misc{", content)
        self.assertIn("Real Study", content)
        self.assertIn("PMID: 36443570", content)
        self.assertNotIn("Fake", content)

    def test_csv_full_ledger(self):
        p = os.path.join(self.tmp, "out.csv")
        vr.export_csv(self._sample_results(), p)
        lines = open(p, encoding="utf-8-sig").read().strip().splitlines()
        self.assertEqual(len(lines), 3)  # header + 2 rows
        self.assertIn("verdict", lines[0])

    def test_main_export_via_cli(self):
        refs_path = os.path.join(self.tmp, "refs.json")
        with open(refs_path, "w", encoding="utf-8") as f:
            json.dump([{"title": "t", "url": "https://www.nature.com/x",
                        "source": "journal", "year": 2025}], f)
        out = os.path.join(self.tmp, "r.md")
        code = vr.main_with_args(["--refs", refs_path, "--out", out,
                                  "--offline", "--export", "bibtex,csv"])
        self.assertEqual(code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "r.bib")))
        self.assertTrue(os.path.exists(os.path.join(self.tmp, "r.csv")))


class TestPubMedEUtilities(unittest.TestCase):
    """在线核验（依赖网络；不可达时跳过）。"""

    def setUp(self):
        try:
            ok, _ = vr.pubmed_pmid_exists("36443570", 8.0)
        except Exception:
            ok = None
        if ok is not True:
            self.skipTest("E-utilities 不可达")

    def test_real_pmid_exists(self):
        ok, note = vr.pubmed_pmid_exists("36443570", 8.0)
        self.assertTrue(ok)
        self.assertIn("核实存在", note)

    def test_fake_pmid_rejected(self):
        ok, note = vr.pubmed_pmid_exists("99999999", 8.0)
        self.assertFalse(ok)
        self.assertIn("编造", note)


if __name__ == "__main__":
    unittest.main(verbosity=2)
