import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from detect_protocol_document import detect
from extract_protocol_components import extract
from validate_protocol_completeness import validate


def complete_components():
    return {
        "background_and_objective": "背景与目的",
        "picos": {"population": "P", "intervention": "I", "comparison": "C", "outcome": "O", "study_design": "S"},
        "study_design": "RCT",
        "eligibility": {"inclusion": ["标准1"], "exclusion": ["标准2"]},
        "sample_size": {"basis": {"method": "two proportions"}},
        "outcomes": {"primary": ["主要终点"], "secondary": ["次要终点"]},
        "statistical_analysis": "ITT",
        "references": ["PMID:1"],
    }


class ProtocolTests(unittest.TestCase):
    def test_complete_routes_s(self):
        self.assertTrue(validate({"components": complete_components()})["valid"])

    def test_nested_empty_values_block(self):
        variants = [
            ("background_and_objective", "   "),
            ("references", [{}]),
            ("outcomes", {"primary": [""], "secondary": [""]}),
            ("sample_size", {"basis": {"method": ""}}),
        ]
        for field, value in variants:
            data = complete_components()
            data[field] = value
            with self.subTest(field=field):
                self.assertFalse(validate({"components": data})["valid"])

    def test_extraction_uncertain_blocks(self):
        report = validate({"components": complete_components(), "extraction_warnings": [{"code": "EXTRACTION_UNCERTAIN"}]})
        self.assertFalse(report["valid"])

    def test_archived_is_not_selected(self):
        report = detect({"artifacts": [{"type": "study_protocol", "name": "protocol.docx", "status": "archived"}]})
        self.assertFalse(report["exists"])

    def test_runtime_exception_cannot_bypass_hardcoded_rule(self):
        data = complete_components()
        data["picos"]["comparison"] = ""
        report = validate({"components": data, "allowed_missing": ["picos.comparison"]})
        self.assertFalse(report["valid"])

    def test_exact_business_outputs(self):
        passed = validate({"components": complete_components()})
        self.assertEqual((passed["validation_result"], passed["branch"], passed["next_node"]), ("完整性校验通过", "S", "0.2"))
        data = complete_components()
        data["references"] = []
        failed = validate({"components": data})
        self.assertEqual(failed["validation_result"], "完整性校验不通过")
        self.assertEqual(failed["branch"], "M")
        self.assertEqual(failed["message"], "方案不完整，缺少：[参考文献列表]")

    def test_markdown_extraction_has_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "protocol.md"
            path.write_text("# 研究背景\n这是研究背景。\n# 研究目的\n验证主要假设。\n# 统计分析\n采用ITT分析。", encoding="utf-8")
            report = extract({"document_path": str(path)})
        self.assertFalse(report["extraction_warnings"])
        self.assertIn("background_and_objective", report["components"])
        self.assertTrue(report["components"]["background_and_objective"]["evidence_locations"])

    def test_missing_document_is_uncertain(self):
        report = extract({"document_path": "Z:/not-found/protocol.pdf"})
        self.assertEqual(report["extraction_warnings"][0]["code"], "EXTRACTION_UNCERTAIN")


if __name__ == "__main__":
    unittest.main()
