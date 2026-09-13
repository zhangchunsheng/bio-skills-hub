import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DETECT_PATH = ROOT / "scripts" / "detect.py"

spec = importlib.util.spec_from_file_location("detect", DETECT_PATH)
detect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect)


def make_sheet(name, page, table_num, columns, headers=None):
    return {
        "name": name,
        "page": page,
        "table_num_on_page": table_num,
        "headers": headers or [f"col_{i}" for i in range(len(columns))],
        "columns": columns,
    }


def flag_types(flags):
    return {flag["type"] for flag in flags}


class DetectTests(unittest.TestCase):
    def test_last_digit_ignores_formatted_trailing_zeroes(self):
        values = [100 + (i % 9 + 1) / 10 for i in range(90)]

        result = detect.last_digit_chi_square(values, "sheet", "mean")

        self.assertIsNone(result)

    def test_report_distinguishes_no_numeric_tables_from_no_anomalies(self):
        report = detect.generate_report(
            {"title": "No tables", "doi": "", "pmid": "", "pages": 2},
            [],
            [],
            "/tmp/no-tables.pdf",
        )

        html = detect.render_html(report)

        self.assertEqual(report["data_status"], "insufficient_data")
        self.assertIn("未提取到可检测的数值表格", html)
        self.assertNotIn("通过了全部", html)

    def test_install_hint_uses_pip_package_names(self):
        hint = detect.build_install_hint(["PyMuPDF (fitz)", "numpy", "pdfplumber"])

        self.assertEqual(hint, "pip install pymupdf numpy pdfplumber")

    def test_cross_engine_duplicate_tables_are_not_cross_table_flags(self):
        columns = [
            [10.1, 11.2, 12.3, 13.4, 14.5, 15.6],
            [20.1, 21.2, 22.3, 23.4, 24.5, 25.6],
        ]
        sheets = [
            make_sheet("Page1_Table1_camelot_stream", 1, 1, columns, ["a", "b"]),
            make_sheet("Page1_Table2_pdfplumber", 1, 2, columns, ["a", "b"]),
        ]

        flags = detect.run_detectors(sheets)

        self.assertNotIn("cross_sheet_identical", flag_types(flags))

    def test_detector_suite_has_nine_active_detectors(self):
        self.assertEqual(detect.ACTIVE_DETECTOR_COUNT, 9)
        self.assertNotIn("check_grim", detect.DETECTOR_FUNCS)

    def test_core_detectors_emit_expected_flags(self):
        self.assertEqual(detect.check_constant_offset([1, 2, 3, 4, 5], [2, 3, 4, 5, 6], "a", "b")["type"], "constant_offset")
        self.assertEqual(detect.check_constant_ratio([1, 2, 3, 4, 5], [2, 4, 6, 8, 10], "a", "b")["type"], "constant_ratio")
        self.assertEqual(detect.check_arithmetic_progression([1.2, 2.4, 3.6, 4.8, 6.0, 7.2, 8.4, 9.6], "x")["type"], "arithmetic_progression")
        self.assertEqual(detect.check_decimal_repetition([1.1234, 2.1234, 3.1234, 4.5678, 5.5678, 6.5678, 7.5678, 8.5678, 9.5678, 10.5678], "x")["type"], "decimal_repetition")
        self.assertEqual(detect.check_rounded_to_grid([1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0], "x")["type"], "rounded_to_grid")
        self.assertEqual(detect.check_benford([9.0 + i * 0.01 for i in range(30)], "x")["type"], "benford_violation")
        self.assertEqual(detect.check_identical_columns([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], "a", "b")["type"], "identical_columns")

    def test_cross_sheet_detector_still_flags_distinct_repeated_tables(self):
        sheet_a = make_sheet("Page1_Table1_camelot_stream", 1, 1, [[i for i in range(1, 8)], [i + 20 for i in range(1, 8)]])
        sheet_b = make_sheet("Page2_Table1_camelot_stream", 2, 1, [[i for i in range(1, 8)], [i + 20 for i in range(1, 8)]])

        flags = detect.run_detectors([sheet_a, sheet_b])

        self.assertIn("cross_sheet_identical", flag_types(flags))


if __name__ == "__main__":
    unittest.main()
