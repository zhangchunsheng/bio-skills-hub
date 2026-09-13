import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_has_no_external_knowledge_base_or_network_dependency(self):
        paths = [ROOT / "SKILL.md", ROOT / "scripts" / "csv_store.py"]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths).casefold()
        self.assertNotIn("http://", combined)
        self.assertNotIn("https://", combined)
        script = self.read("scripts/csv_store.py").casefold()
        for network_api in ("requests", "urllib", "http.client", "socket"):
            self.assertNotIn(network_api, script)

    def test_skill_references_required_resources(self):
        skill = self.read("SKILL.md")
        self.assertIn("references/three-layer-method.md", skill)
        self.assertIn("references/medical-safety.md", skill)
        self.assertIn("scripts/csv_store.py", skill)

    def test_skill_requires_specialty_and_csv_output(self):
        skill = self.read("SKILL.md")
        for phrase in (
            "科室/专业方向",
            "CSV",
            "默认 30",
            "序号",
            "选题标题",
            "第一层关键词",
            "第二层关键词",
            "第三层关键词",
            "生成模式",
            "生成日期",
        ):
            self.assertIn(phrase, skill)
        self.assertNotIn("TODO", skill)

    def test_three_layer_roles_are_preserved(self):
        method = self.read("references/three-layer-method.md")
        for phrase in ("内容对象", "使用语境", "提问角度", "目标数量 × 4"):
            self.assertIn(phrase, method)

    def test_medical_safety_blocks_diagnosis_and_promises(self):
        safety = self.read("references/medical-safety.md")
        for phrase in ("治疗效果承诺", "个体诊断", "处方", "停药", "延误就医", "虚构证据"):
            self.assertIn(phrase, safety)

    def test_platform_rules_are_limited_to_medical_topic_filtering(self):
        safety = self.read("references/medical-safety.md")
        for phrase in (
            "抖音与视频号医疗选题补充过滤",
            "医疗谣言",
            "偏方",
            "高风险医疗操作",
            "患者故事",
            "震惊体",
            "问诊互动",
            "站外导流",
            "恶性肿瘤治疗",
        ):
            self.assertIn(phrase, safety)
        for unrelated_rule in ("执业证书编号", "直播资质", "AIGC 标识", "电商规则"):
            self.assertNotIn(unrelated_rule, safety)

    def test_agent_interface_metadata(self):
        interface = self.read("agents/interface.yaml")
        for phrase in ("医生IP三层选题", "$medical-three-layer-topic"):
            self.assertIn(phrase, interface)

    def test_release_metadata_forbids_remote_inline_execution(self):
        for relative_path in ("agents/interface.yaml",):
            content = self.read(relative_path)
            self.assertIn('canonical_format: "agent-skills"', content)
            self.assertIn('remote_inline_execution: "forbid"', content)
            self.assertIn('source_tier: "local"', content)

        policy = json.loads(self.read("security/permission_policy.json"))
        approval = policy["capabilities"]["file_write"]
        self.assertEqual(approval["decision"], "approved")
        self.assertIn("output directory", approval["scope"])


if __name__ == "__main__":
    unittest.main()
