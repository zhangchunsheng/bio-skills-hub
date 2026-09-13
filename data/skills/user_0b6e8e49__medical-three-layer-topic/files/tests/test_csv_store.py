import csv
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path

from scripts.csv_store import (
    LIBRARY_HEADERS,
    TOPIC_HEADERS,
    CsvStoreError,
    main,
    sanitize_specialty,
    write_library,
    write_topics,
)


class CsvStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    @staticmethod
    def topic(title="体检发现血糖偏高，复查时要看哪些指标？"):
        return {
            "title": title,
            "layer1": "空腹血糖",
            "layer2": "体检发现",
            "layer3": "需要复查吗",
            "mode": "mixed",
        }

    def read_csv(self, path):
        with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            return reader.fieldnames, list(reader)

    def test_topics_csv_has_bom_exact_headers_and_quoted_text(self):
        title = '血糖偏高，医生说“先复查”，到底看什么？'
        output = write_topics(
            {"topics": [self.topic(title)]},
            "内分泌科",
            self.output_dir,
            date(2026, 7, 20),
        )

        self.assertEqual(output.read_bytes()[:3], b"\xef\xbb\xbf")
        headers, rows = self.read_csv(output)
        self.assertEqual(headers, TOPIC_HEADERS)
        self.assertEqual(rows[0]["选题标题"], title)
        self.assertEqual(rows[0]["序号"], "1")
        self.assertEqual(rows[0]["生成日期"], "2026-07-20")

    def test_topic_history_skips_existing_and_batch_duplicates(self):
        old_title = "体检发现血糖偏高，复查时要看哪些指标？"
        new_title = "刚开始用二甲双胍，日常需要注意什么？"
        write_topics(
            {"topics": [self.topic(old_title)]},
            "内分泌科",
            self.output_dir,
            date(2026, 7, 19),
        )

        output = write_topics(
            {"topics": [self.topic(old_title), self.topic(old_title), self.topic(new_title)]},
            "内分泌科",
            self.output_dir,
            date(2026, 7, 20),
        )

        _, result_rows = self.read_csv(output)
        _, history_rows = self.read_csv(self.output_dir / "选题历史.csv")
        self.assertEqual([row["选题标题"] for row in result_rows], [new_title])
        self.assertEqual([row["选题标题"] for row in history_rows], [old_title, new_title])

    def test_corrupt_history_is_preserved_and_write_aborts(self):
        history = self.output_dir / "选题历史.csv"
        history.write_text("错误表头\n原始内容\n", encoding="utf-8-sig")
        original_bytes = history.read_bytes()

        with self.assertRaises(CsvStoreError):
            write_topics(
                {"topics": [self.topic()]},
                "内分泌科",
                self.output_dir,
                date(2026, 7, 20),
            )

        self.assertEqual(history.read_bytes(), original_bytes)
        self.assertFalse((self.output_dir / "医生IP选题_内分泌科_20260720.csv").exists())

    def test_specialty_cannot_escape_output_directory(self):
        safe_name = sanitize_specialty("../../内分泌科\\bad")
        self.assertNotIn("/", safe_name)
        self.assertNotIn("\\", safe_name)
        self.assertNotIn("..", safe_name)

        output = write_library(
            {
                "keywords": [
                    {"layer": "L1", "keyword": "糖尿病", "category": "疾病", "weight": 5, "status": "启用"}
                ]
            },
            "../../内分泌科\\bad",
            self.output_dir,
        )
        self.assertEqual(output.resolve().parent, self.output_dir.resolve())

    def test_library_csv_has_exact_headers_and_bom(self):
        output = write_library(
            {
                "keywords": [
                    {"layer": "L1", "keyword": "糖化血红蛋白", "category": "检查指标", "weight": 5, "status": "启用"}
                ]
            },
            "内分泌科",
            self.output_dir,
        )

        self.assertEqual(output.read_bytes()[:3], b"\xef\xbb\xbf")
        headers, rows = self.read_csv(output)
        self.assertEqual(headers, LIBRARY_HEADERS)
        self.assertEqual(rows[0]["关键词"], "糖化血红蛋白")

    def test_cli_rejects_missing_fields_without_partial_file(self):
        input_path = self.output_dir / "invalid.json"
        input_path.write_text(
            json.dumps({"topics": [{"title": "缺字段", "layer1": "血糖", "layer2": "复查", "mode": "mixed"}]}),
            encoding="utf-8",
        )

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(
                [
                    "topics",
                    "--input",
                    str(input_path),
                    "--specialty",
                    "内分泌科",
                    "--output-dir",
                    str(self.output_dir),
                    "--date",
                    "2026-07-20",
                ]
            )

        self.assertNotEqual(exit_code, 0)
        self.assertIn("layer3", stderr.getvalue())
        self.assertEqual(list(self.output_dir.glob("医生IP选题_*.csv")), [])
        self.assertFalse((self.output_dir / "选题历史.csv").exists())


if __name__ == "__main__":
    unittest.main()
