# 标准化方案组件 Schema

```json
{
  "protocol_artifact_id": "ART-001",
  "rule_set": "protocol-completeness-v1",
  "components": {
    "background_and_objective": {},
    "picos": {
      "population": {},
      "intervention": {},
      "comparison": {},
      "outcome": {},
      "study_design": {}
    },
    "study_design": {},
    "eligibility": {"inclusion": [], "exclusion": []},
    "sample_size": {"basis": {}, "result": null},
    "outcomes": {"primary": [], "secondary": []},
    "statistical_analysis": {},
    "references": []
  },
  "extraction_warnings": []
}
```

抽取器应为每个非空组件保留原文证据位置。证据位置可作为组件对象的 `evidence_locations` 字段，不参与空值判断。
